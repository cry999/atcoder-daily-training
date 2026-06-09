package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/selfupdate"
)

// cmdUpdate は最新版を確認し、現在版と違えば `go install …@latest` で入れ替える。
// --check のときは確認だけ行いインストールしない。最新版の解決・install には
// go ツールチェインとネットワークが要る。
func cmdUpdate(args []string) (int, error) {
	flags := flag.NewFlagSet("update", flag.ContinueOnError)
	check := flags.Bool("check", false, "Only check whether a newer version exists; do not install")
	local := flags.Bool("local", false, "Install from the local ./cmd/atcoder working tree instead of @latest")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args); err != nil {
		return 2, err
	}
	if *local && *check {
		return 2, errors.New("--local and --check cannot be combined")
	}

	cur := selfupdate.ReadCurrent()
	ctx := context.Background()

	// --local: cwd の作業ツリーから直接インストールする。最新解決・network 不要で、
	// 未 push のローカルコミットもそのまま反映できる (cwd がリポジトリ内である前提)。
	if *local {
		fmt.Printf("  current  %s\n", describeCurrent(cur))
		fmt.Println("  installing… go install ./cmd/atcoder")
		if err := selfupdate.InstallLocal(ctx, os.Stderr); err != nil {
			return 1, err
		}
		fmt.Println("  installed from local working tree ✓")
		return 0, nil
	}

	latest, err := selfupdate.ResolveLatest(ctx, cur.Module)
	if err != nil {
		return 1, err
	}

	fmt.Printf("  current  %s\n", describeCurrent(cur))
	fmt.Printf("  latest   %s\n", describeLatest(latest))
	if cur.Modified {
		fmt.Println("  note: built from a modified tree; version comparison may be unreliable")
	}

	available := selfupdate.Available(cur, latest)

	if *check {
		if available {
			fmt.Println("  update available — run `atcoder update`")
		} else {
			fmt.Println("  up to date")
		}
		return 0, nil
	}

	if !available {
		fmt.Printf("  already up to date (%s)\n", latestRef(latest))
		return 0, nil
	}

	fmt.Printf("  installing… go install %s/cmd/atcoder@latest\n", cur.Module)
	if err := selfupdate.Install(ctx, cur.Module, os.Stderr); err != nil {
		return 1, err
	}
	fmt.Printf("  installed %s ✓\n", latestRef(latest))
	return 0, nil
}

// describeLatest は最新版を "<sha-or-version> (<time>)" 形式の文字列にする。
func describeLatest(l selfupdate.Latest) string {
	s := latestRef(l)
	if !l.Time.IsZero() {
		s += " (" + l.Time.Format(time.RFC3339) + ")"
	}
	return s
}

// latestRef は最新版の短い識別子 (pseudo-version なら短縮 sha、タグ版なら版文字列)。
func latestRef(l selfupdate.Latest) string {
	if l.Sha != "" {
		return l.Sha
	}
	return l.Version
}
