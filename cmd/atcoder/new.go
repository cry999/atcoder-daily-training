package main

import (
	"errors"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cliargs"
	"github.com/cry999/atcoder-daily-training/internal/contestmeta"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

// fetchInterval は一括 fetch でタスク間に挟む待機。AtCoder への連続アクセスで
// rate limit を踏まないための保険 (ネットワーク取得が起きたケースの後だけ待つ)。
const fetchInterval = 300 * time.Millisecond

// cmdNew は引数なしなら当日 dir を作り、`abc <contest>` ならコンテスト一括準備を行う。
func cmdNew(args []string) error {
	if len(args) == 0 {
		return newToday()
	}
	switch args[0] {
	case "abc":
		return newABC(args[1:])
	default:
		return fmt.Errorf("unknown new mode %q (want: abc, or no argument for today's dir)", args[0])
	}
}

// newToday は当日の練習ディレクトリ exercise/YYYY/MM/DD を作成する (従来挙動)。
func newToday() error {
	y, m, d := time.Now().Local().Date()
	dirname := filepath.Join(
		"exercise",
		fmt.Sprintf("%04d", y),
		fmt.Sprintf("%02d", m),
		fmt.Sprintf("%02d", d),
	)
	if _, err := os.Stat(dirname); errors.Is(err, fs.ErrNotExist) {
		if err := os.MkdirAll(dirname, 0o755); err != nil {
			return fmt.Errorf("failed to create exercise directory: %w", err)
		}
		fmt.Printf("Created new exercise directory: %s\n", dirname)
		return nil
	} else if err != nil {
		return err
	}
	fmt.Printf("Exercise directory already exists: %s\n", dirname)
	return nil
}

// newABC は ABC コンテスト 1 つ分を一括準備する:
// タスク一覧 + サンプルの fetch、コンテストメタ保存、解答スケルトン生成。
func newABC(args []string) error {
	flagArgs, positionals := cliargs.Split(args)
	if len(positionals) < 1 {
		return errors.New("contest is required (e.g. `atcoder new abc abc457`)")
	}
	contest := positionals[0]

	fs := flag.NewFlagSet("new abc", flag.ContinueOnError)
	refresh := fs.Bool("refresh", false, "Re-fetch samples and contest meta, overwriting the cache")
	tasksFlag := fs.String("tasks", "", `Limit to these tasks (comma-separated letters or task IDs, e.g. "a,b" or "abc457_a")`)
	noSkeleton := fs.Bool("no-skeleton", false, "Do not generate solution skeleton files")
	noFetch := fs.Bool("no-fetch", false, "Skip all network fetches (samples and contest meta)")
	fs.SetOutput(os.Stderr)
	if err := fs.Parse(flagArgs); err != nil {
		return err
	}

	if _, ok := layout.ContestNum(contest); !ok {
		return fmt.Errorf("contest ID must match abc<NNN>, got %q", contest)
	}

	// --tasks 指定はタスク ID に展開する (letter 単体は <contest>_<letter> へ)。
	var wantTasks []string
	for _, p := range strings.Split(*tasksFlag, ",") {
		if p = strings.TrimSpace(p); p != "" {
			wantTasks = append(wantTasks, layout.TaskID(contest, p))
		}
	}

	cm, err := resolveContestMeta(contest, wantTasks, *refresh, *noFetch)
	if err != nil {
		return err
	}

	// 処理対象タスク: --tasks 指定があればその部分集合、無ければメタの全タスク。
	tasks := wantTasks
	if len(tasks) == 0 {
		tasks = cm.Tasks
	}
	if len(tasks) == 0 {
		return errors.New("no tasks to prepare")
	}

	printContestHeader(cm)

	var fetchErr error
	if !*noFetch {
		fetchErr = fetchTasks(contest, tasks, *refresh)
	}

	if !*noSkeleton {
		if err := generateSkeletons(contest, tasks); err != nil {
			return err
		}
	}

	if fetchErr != nil {
		return fetchErr
	}
	fmt.Printf("ready. run: atcoder test %s --task %s\n", contest, firstLetter(tasks))
	return nil
}

// resolveContestMeta は contest.toml を解決する。
//   - --no-fetch: キャッシュ済みを使う。無ければ --tasks から最小メタを組んで保存。
//   - キャッシュ済み && !refresh: そのまま使う。
//   - それ以外: ネットワークから取得して保存。
func resolveContestMeta(contest string, wantTasks []string, refresh, noFetch bool) (*contestmeta.Meta, error) {
	metaPath := contestmeta.Path(contest)
	cached, _ := contestmeta.Load(metaPath) // 未キャッシュなら err、cached=nil

	switch {
	case noFetch:
		if cached != nil {
			return cached, nil
		}
		if len(wantTasks) == 0 {
			return nil, errors.New("--no-fetch needs a cached contest.toml or --tasks to know the task list")
		}
		cm := &contestmeta.Meta{
			Contest: contest,
			URL:     "https://atcoder.jp/contests/" + contest,
			Tasks:   wantTasks,
		}
		if err := contestmeta.Save(metaPath, cm); err != nil {
			return nil, err
		}
		return cm, nil
	case cached != nil && !refresh:
		return cached, nil
	default:
		fmt.Printf("fetching contest meta for %s ...\n", contest)
		cm, err := contestmeta.Fetch(contest)
		if err != nil {
			return nil, fmt.Errorf("failed to fetch contest meta: %w", err)
		}
		if err := contestmeta.Save(metaPath, cm); err != nil {
			return nil, err
		}
		return cm, nil
	}
}

// fetchTasks は各タスクのサンプル + meta をキャッシュに揃え、進捗を表示する。
// 1 件でも失敗したらまとめてエラーを返す (成功分のキャッシュは残る)。
func fetchTasks(contest string, tasks []string, refresh bool) error {
	var rep testexec.Reporter = quietReporter{}
	fmt.Printf("fetching %d task(s) ...\n", len(tasks))
	failed := 0
	for i, tid := range tasks {
		res, err := testexec.EnsureTests(rep, contest, tid, refresh)
		if err != nil {
			fmt.Printf("  [%d/%d] %s  FAILED: %v\n", i+1, len(tasks), tid, err)
			failed++
			continue
		}
		status := "cached"
		if res.Fetched {
			status = fmt.Sprintf("fetched, %d samples", res.NumSamples)
		}
		fmt.Printf("  [%d/%d] %s  ok (%s)\n", i+1, len(tasks), tid, status)
		// ネットワーク取得が起きたときだけ、次のタスクまで少し待つ。
		if res.Fetched && i < len(tasks)-1 {
			time.Sleep(fetchInterval)
		}
	}
	if failed > 0 {
		return fmt.Errorf("%d/%d task(s) failed to fetch", failed, len(tasks))
	}
	return nil
}

// generateSkeletons は各タスクの解答ファイル abc/<num>/<letter>.py を、
// 存在しなければ空ファイルで作成する (既存ファイルは温存する)。
func generateSkeletons(contest string, tasks []string) error {
	lay := layout.ABC{}
	created, existed := 0, 0
	for _, tid := range tasks {
		path, err := lay.SolutionPath(contest, tid)
		if err != nil {
			return err
		}
		if _, err := os.Stat(path); err == nil {
			existed++
			continue
		}
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			return err
		}
		if err := os.WriteFile(path, nil, 0o644); err != nil {
			return err
		}
		created++
	}
	fmt.Printf("skeleton: %d created, %d already existed\n", created, existed)
	return nil
}

func printContestHeader(cm *contestmeta.Meta) {
	name := cm.Title
	if name == "" {
		name = cm.Contest
	}
	fmt.Printf("contest %s — %s\n", cm.Contest, name)
	if !cm.StartAt.IsZero() && !cm.EndAt.IsZero() {
		s := cm.StartAt.Local()
		e := cm.EndAt.Local()
		fmt.Printf("  %s – %s (%dm)\n", s.Format("2006-01-02 15:04"), e.Format("15:04"), cm.DurationMs/60000)
	}
}

// firstLetter は readiness ヒント用に最初のタスクの letter を返す。
func firstLetter(tasks []string) string {
	if len(tasks) == 0 {
		return "a"
	}
	if l, err := layout.Letter(tasks[0]); err == nil {
		return l
	}
	return tasks[0]
}

// quietReporter は testexec.EnsureTests に渡す無出力 Reporter。
// 進捗は newABC 側が自前で表示するため、すべて no-op にする。
type quietReporter struct{}

func (quietReporter) Fetching(contest, task string)                                                {}
func (quietReporter) Header(task, contest string, timeLimitMs, timeoutMs, ntests int, tol float64) {}
func (quietReporter) Begin(names []string, jobs int)                                               {}
func (quietReporter) CaseStarted(name string)                                                      {}
func (quietReporter) CaseFinished(cr testexec.CaseResult)                                          {}
func (quietReporter) End(results []testexec.CaseResult)                                            {}
func (quietReporter) Summary(passed, total int)                                                    {}
