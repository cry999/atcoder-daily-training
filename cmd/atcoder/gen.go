package main

import (
	"errors"
	"flag"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/cliargs"
	"github.com/cry999/atcoder-daily-training/internal/extracase"
	"github.com/cry999/atcoder-daily-training/internal/gen"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
	"github.com/cry999/atcoder-daily-training/internal/ui"
)

// cmdGen は `atcoder gen <contest> --task <letter> ...` を捌く (要件 060)。
// 問題の制約 / 入力形式をベストエフォートで認識し、それを満たすランダム入力を
// 生成する。出力の正しさは検証しない (入力を作るだけ)。解答ファイルには触れない。
func cmdGen(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	if len(positionals) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := positionals[0]

	fs := flag.NewFlagSet("gen", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	taskFlag := addTaskFlag(fs)
	var count int
	fs.IntVar(&count, "count", 1, "Number of inputs to generate.")
	fs.IntVar(&count, "n", 1, "Number of inputs to generate.")
	outPath := fs.String("out", "", "Write to file(s) instead of stdout. With -n>1, treated as a directory (01.in, 02.in, ...).")
	fs.StringVar(outPath, "o", "", "Write to file(s) instead of stdout. With -n>1, treated as a directory (01.in, 02.in, ...).")
	save := fs.Bool("save", false, "Also save each generated input into tests-extra/ as an input-only case (empty .out).")
	sizeStr := fs.String("size", "random", "Input size: random (default) | max (all sizes at their upper bound, for TLE probing) | min.")
	var seed int64
	fs.Int64Var(&seed, "seed", 0, "Random seed for reproducible generation. Unset → time-based.")
	showSpec := fs.Bool("show-spec", false, "Print the recognized spec (variables, ranges, warnings) instead of generating.")
	refresh := fs.Bool("refresh", false, "Re-fetch and overwrite the cached constraints/input-format sections (cache only).")
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}

	if *taskFlag == "" {
		return 2, errors.New("--task is required")
	}
	task := layout.TaskID(contest, *taskFlag)

	set := map[string]bool{}
	fs.Visit(func(f *flag.Flag) { set[f.Name] = true })
	// --show-spec は生成系フラグと排他 (認識結果の確認に専念)。
	if *showSpec {
		if setAnyOf(set, "count", "n", "out", "o", "save", "size", "seed") {
			return 2, errors.New("--show-spec cannot be combined with -n/--out/--save/--size/--seed")
		}
	}
	if count < 1 {
		return 2, errors.New("--count must be >= 1")
	}
	size, err := gen.ParseSizeMode(*sizeStr)
	if err != nil {
		return 2, err
	}

	// 生セクションを用意する (キャッシュ or fetch)。取得進捗は握りつぶす。
	raw, err := testexec.EnsureGenSource(ui.NewTestReporter(false, false, false), contest, task, *refresh)
	if err != nil {
		return 1, err
	}
	spec, err := gen.ParseSpec(*raw)
	if err != nil {
		return 1, err
	}

	if *showSpec {
		fmt.Print(spec.Describe())
		return 0, nil
	}

	// 取りこぼし警告は stderr に出す (生成は続行、exit 0)。
	for _, w := range spec.Warnings {
		fmt.Fprintln(os.Stderr, "warning:", w)
	}

	src := rand.NewSource(seed)
	if !set["seed"] {
		src = rand.NewSource(time.Now().UnixNano())
	}
	rng := rand.New(src)

	taskDir := cachepath.Task(contest, task)
	for i := 1; i <= count; i++ {
		input, err := spec.Generate(rng, size)
		if err != nil {
			return 1, err
		}
		if err := emitGen(input, *outPath, i, count); err != nil {
			return 1, err
		}
		if *save {
			name, err := extracase.Save(taskDir, "", input, []byte{})
			if err != nil {
				return 1, err
			}
			fmt.Fprintf(os.Stderr, "saved tests-extra/%s (input-only case)\n", name)
		}
	}
	return 0, nil
}

// emitGen は 1 件の生成入力を stdout か --out 先に書き出す。
// --out 指定かつ count>1 のときは out をディレクトリ扱いし NN.in を書く。
func emitGen(input []byte, outPath string, idx, count int) error {
	if outPath == "" {
		os.Stdout.Write(input)
		return nil
	}
	if count == 1 {
		return os.WriteFile(outPath, input, 0o644)
	}
	if err := os.MkdirAll(outPath, 0o755); err != nil {
		return err
	}
	name := fmt.Sprintf("%02d.in", idx)
	return os.WriteFile(filepath.Join(outPath, name), input, 0o644)
}

// setAnyOf は set のいずれかのキーが立っているかを返す。
func setAnyOf(set map[string]bool, names ...string) bool {
	for _, n := range names {
		if set[n] {
			return true
		}
	}
	return false
}
