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

	// --check: installed / local / remote の 3 基準点と remote・local の 2 判定を
	// 表示するだけ (入れ替えはしない)。リモート解決に失敗しても local までは出す。
	if *check {
		return runCheck(ctx, cur)
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

// runCheck は `atcoder update --check`。installed / local / remote の 3 基準点と、
// remote (installed ⇄ @latest) ・ local (installed ⇄ 作業ツリー HEAD) の 2 判定を
// 表示する。リモート解決に失敗しても local 行と local 判定までは出してから
// exit 1 を返す (リモート確認は要件 050 どおり実行時失敗扱い)。
func runCheck(ctx context.Context, cur selfupdate.Current) (int, error) {
	local := selfupdate.ReadLocalSource(ctx)
	latest, rerr := selfupdate.ResolveLatest(ctx, cur.Module)

	fmt.Printf("  installed  %s\n", describeCurrent(cur))
	fmt.Printf("  local      %s\n", describeLocal(local))
	if rerr == nil {
		fmt.Printf("  remote     %s\n", describeLatest(latest))
	}
	fmt.Println()

	if rerr == nil {
		fmt.Println("  remote: " + remoteVerdict(cur, latest))
	}
	fmt.Println("  local:  " + localVerdict(cur, local))

	if rerr != nil {
		// installed/local までは見せた上で、リモート解決失敗は exit 1。
		// main が "atcoder update: <err>" を stderr に出す。
		return 1, rerr
	}
	return 0, nil
}

// remoteVerdict は installed ⇄ remote(@latest) の関係を一行に整形する。
func remoteVerdict(cur selfupdate.Current, latest selfupdate.Latest) string {
	switch selfupdate.ClassifyRemote(cur, latest) {
	case selfupdate.RemoteUpToDate:
		return "up to date"
	case selfupdate.RemoteInstalledNewer:
		return "up to date (installed is newer than origin)"
	case selfupdate.RemoteUpdateAvailable:
		return "update available — run `atcoder update`"
	default: // RemoteIndeterminate
		return "cannot compare (installed version unknown)"
	}
}

// localVerdict は installed ⇄ 作業ツリー HEAD の関係を一行に整形する。
func localVerdict(cur selfupdate.Current, local selfupdate.LocalSource) string {
	if !local.Known {
		return "n/a — run inside the repo to compare with local source"
	}
	available, reason := selfupdate.LocalUpdate(cur, local)
	if available {
		return "rebuild available — run `atcoder update --local` (" + reason + ")"
	}
	return "up to date (" + reason + ")"
}

// describeLocal は作業ツリー版を "<short-sha> (<time>)[ dirty]" 形式にする。
// 作業ツリーを読めなければ "n/a (...)"。
func describeLocal(l selfupdate.LocalSource) string {
	if !l.Known {
		return "n/a (not in a repo working tree)"
	}
	s := l.ShortRev()
	if !l.Time.IsZero() {
		s += " (" + l.Time.Format(time.RFC3339) + ")"
	}
	if l.Dirty {
		s += " dirty"
	}
	return s
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
