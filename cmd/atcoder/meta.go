package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/cliargs"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
	"github.com/cry999/atcoder-daily-training/internal/ui"
)

// cmdMeta は `atcoder meta <fetch|show|set> ...` を捌く (要件 046)。
// キャッシュ層 (meta.toml + tests/) の準備・点検・補正に専念し、judge も
// 解答スケルトン生成も行わない。
func cmdMeta(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("usage: atcoder meta <fetch|show|set> <url | contest --task <task>>")
	}
	sub, rest := args[0], args[1:]
	switch sub {
	case "fetch":
		return metaFetch(rest)
	case "show":
		return metaShow(rest)
	case "set":
		return metaSet(rest)
	default:
		return 2, fmt.Errorf("unknown meta subcommand %q (want fetch|show|set)", sub)
	}
}

// resolveMetaTarget は meta 共通のターゲット指定を解決する。
// 位置引数が task URL なら URL から contest_id / task_id を抽出し、それ以外は
// contest 位置引数 + --task (短縮形展開) を使う。
func resolveMetaTarget(positionals []string, taskFlag string) (contest, task string, err error) {
	if len(positionals) >= 1 && layout.IsTaskURL(positionals[0]) {
		c, t, ok := layout.ParseTaskURL(positionals[0])
		if !ok {
			return "", "", fmt.Errorf("task URL を解釈できません: %s", positionals[0])
		}
		return c, t, nil
	}
	if len(positionals) < 1 {
		return "", "", errors.New("contest または task URL が必要です")
	}
	contest = positionals[0]
	if taskFlag == "" {
		return "", "", errors.New("--task が必要です (または task URL を渡してください)")
	}
	return contest, layout.TaskID(contest, taskFlag), nil
}

// metaFetch は task のサンプル + Time Limit を AtCoder から取得しキャッシュへ
// 書き込む (強制再取得)。解答ファイルの有無は問わない。
func metaFetch(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	fs := flag.NewFlagSet("meta fetch", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	taskFlag := addTaskFlag(fs)
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}
	contest, task, err := resolveMetaTarget(positionals, *taskFlag)
	if err != nil {
		return 2, err
	}

	reporter := ui.NewTestReporter(false, false)
	res, err := testexec.EnsureTests(reporter, contest, task, true)
	if err != nil {
		return 1, err
	}
	m, err := testexec.LoadMeta(contest, task)
	if err != nil {
		return 1, err
	}
	fmt.Printf("fetched %s\n", task)
	fmt.Printf("  url:         %s\n", m.URL)
	fmt.Printf("  time limit:  %d ms\n", res.TimeLimitMs)
	fmt.Printf("  samples:     %d\n", res.NumSamples)
	fmt.Printf("  cached at:   %s\n", cachepath.Task(contest, task))
	return 0, nil
}

// metaShow はキャッシュ済み meta.toml を表示する (fetch はしない)。
func metaShow(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	fs := flag.NewFlagSet("meta show", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	taskFlag := addTaskFlag(fs)
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}
	contest, task, err := resolveMetaTarget(positionals, *taskFlag)
	if err != nil {
		return 2, err
	}

	m, err := testexec.LoadMeta(contest, task)
	if err != nil {
		return 1, fmt.Errorf("未キャッシュです (先に `atcoder meta fetch` してください): %s/%s", contest, task)
	}
	n, _ := testexec.SampleCount(contest, task)
	fmt.Printf("%s\n", task)
	fmt.Printf("  url:         %s\n", m.URL)
	fmt.Printf("  time limit:  %d ms\n", m.TimeLimitMs)
	fmt.Printf("  samples:     %d\n", n)
	fmt.Printf("  fetched at:  %s\n", m.FetchedAt.Format(time.RFC3339))
	return 0, nil
}

// metaSet はキャッシュ済み meta.toml の特定フィールドを上書きする。
// 現状は --time-limit (time_limit_ms) のみ。
func metaSet(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	fs := flag.NewFlagSet("meta set", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	taskFlag := addTaskFlag(fs)
	timeLimit := fs.Duration("time-limit", 0, "Override the cached time limit (e.g. 5s, 1500ms). Must be > 0.")
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}
	contest, task, err := resolveMetaTarget(positionals, *taskFlag)
	if err != nil {
		return 2, err
	}

	// 明示されたフィールドだけ上書きする。1 つも無ければフラグ誤り。
	set := map[string]bool{}
	fs.Visit(func(f *flag.Flag) { set[f.Name] = true })
	if !set["time-limit"] {
		return 2, errors.New("更新するフィールドがありません (--time-limit を指定してください)")
	}
	if set["time-limit"] && *timeLimit <= 0 {
		return 2, errors.New("--time-limit は正の値で指定してください (例: 5s, 1500ms)")
	}

	m, err := testexec.LoadMeta(contest, task)
	if err != nil {
		return 1, fmt.Errorf("未キャッシュです (先に `atcoder meta fetch` してください): %s/%s", contest, task)
	}

	oldMs := m.TimeLimitMs
	newMs := int(*timeLimit / time.Millisecond)
	m.TimeLimitMs = newMs
	if err := testexec.SaveMeta(contest, task, m); err != nil {
		return 1, err
	}
	fmt.Printf("updated %s\n", task)
	fmt.Printf("  time limit:  %d ms -> %d ms\n", oldMs, newMs)
	return 0, nil
}
