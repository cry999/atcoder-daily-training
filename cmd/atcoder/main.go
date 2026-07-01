package main

import (
	"fmt"
	"os"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/alias"
	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/selfupdate"
	"github.com/cry999/atcoder-daily-training/internal/usagelog"
)

// builtins は組み込みサブコマンド名の集合。下の switch・usage() と同期させること。
// alias より常に優先される (alias は未知名のときだけ解決される)。
var builtins = map[string]bool{
	"new": true, "start": true, "test": true, "gen": true, "meta": true, "stats": true, "review": true,
	"config": true, "commit": true, "completion": true,
	"update": true, "version": true, "usage": true, "__complete": true,
}

func isBuiltin(name string) bool { return builtins[name] }

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}

	args, err := resolveAlias(os.Args[1:])
	if err != nil {
		fmt.Fprintln(os.Stderr, "atcoder:", err)
		os.Exit(2)
	}

	name := args[0]
	// __complete は補完ヘルパ。シェルが tab ごとに呼ぶのでテレメトリ対象外。即実行。
	if name == "__complete" {
		code, _ := cmdComplete(args[1:])
		os.Exit(code)
	}

	// dispatch を実行前後でラップして利用イベントを記録する (要件 037)。
	// 記録は best-effort で、失敗してもコマンド本体・exit code には影響させない。
	started := time.Now()
	code := dispatch(name, args[1:])
	recordUsage(name, args[1:], code, started)
	os.Exit(code)
}

// dispatch はサブコマンドを実行し exit code を返す。エラー時は従来どおり
// "atcoder <cmd>: <err>" を stderr に出す。未知コマンドは usage を出して 2。
func dispatch(name string, rest []string) int {
	switch name {
	case "new":
		if err := cmdNew(rest); err != nil {
			fmt.Fprintln(os.Stderr, "atcoder new:", err)
			return 1
		}
		return 0
	case "start":
		return runCmd("start", cmdStart, rest)
	case "test":
		return runCmd("test", cmdTest, rest)
	case "gen":
		return runCmd("gen", cmdGen, rest)
	case "meta":
		return runCmd("meta", cmdMeta, rest)
	case "stats":
		return runCmd("stats", cmdStats, rest)
	case "review":
		return runCmd("review", cmdReview, rest)
	case "config":
		return runCmd("config", cmdConfig, rest)
	case "commit":
		return runCmd("commit", cmdCommit, rest)
	case "completion":
		return runCmd("completion", cmdCompletion, rest)
	case "update":
		return runCmd("update", cmdUpdate, rest)
	case "version":
		return runCmd("version", cmdVersion, rest)
	case "usage":
		return runCmd("usage", cmdUsage, rest)
	default:
		usage()
		return 2
	}
}

// runCmd は (int, error) 形のサブコマンドを呼び、エラーを整形して exit code を返す。
func runCmd(name string, fn func([]string) (int, error), rest []string) int {
	code, err := fn(rest)
	if err != nil {
		fmt.Fprintln(os.Stderr, "atcoder "+name+":", err)
	}
	return code
}

// recordUsage は 1 実行分の利用イベントを記録する (non-fatal)。
// 未知コマンド (dispatch が usage を出して 2) は組み込みでないので記録しない。
func recordUsage(name string, rest []string, code int, started time.Time) {
	if !isBuiltin(name) {
		return
	}
	_ = usagelog.Record(usagelog.Event{
		TS:      started,
		Cmd:     name,
		Flags:   usagelog.FlagsFromArgs(rest),
		DurMs:   time.Since(started).Milliseconds(),
		Exit:    code,
		Version: describeCurrent(selfupdate.ReadCurrent()),
	})
}

// resolveAlias は先頭が組み込みでなければ config の [alias] で展開する。
// 組み込みなら config を読まずに即返す (高速・config 文法エラーでも組み込みは動く)。
func resolveAlias(args []string) ([]string, error) {
	if len(args) == 0 || isBuiltin(args[0]) {
		return args, nil
	}
	aliases, err := config.Aliases()
	if err != nil {
		return nil, err // 既存 config.toml の文法エラー
	}
	if len(aliases) == 0 {
		return args, nil
	}
	return alias.Expand(args, aliases, isBuiltin)
}

func usage() {
	fmt.Fprintln(os.Stderr, `Usage:
  atcoder new
  atcoder new abc <contest> [--tasks <list>] [--refresh] [--no-skeleton] [--no-fetch]
  atcoder start  <contest> --task <task> [--until-pass] [--refresh] [-d] [-s] [-j <n>] [--timeout <dur>] [--tolerance <eps>] [--layout <auto|abc|exercise>]
  atcoder test   <contest> --task <task>   # default: judge downloaded samples
                 [sample: -c <N[,M,...]> | --refresh | -j <n> | -w | -s | --json | --submit [--no-open] [--keep-debug]]
                 [ad-hoc: --in <path>|- | --out <path> | --interactive [-R|--auto-restart]]
                 [-v] [-d] [--timeout <dur>] [--tolerance <eps>] [--layout <auto|abc|exercise>]
  atcoder gen    <contest> --task <task>   # 制約・入力形式を認識してランダム入力を生成 (ベストエフォート)
                 [-n <count>] [-o <path>] [--save] [--size <random|max|min>] [--seed <n>] [--show-spec] [--refresh]
  atcoder meta   <fetch | show | set> <url | contest --task <task>>   # キャッシュ (samples + time limit) の DL / 表示 / 編集
                 [set: --url <url> | --time-limit <dur>]
  atcoder stats  [-w|--week | -m|--month | -y|--year | -l|--last <dur>] [-g|--graph]
  atcoder usage  [--flags] [--json]   # ローカルに記録した CLI 利用頻度・所要時間の集計
  atcoder review <category> [-w|--week | -m|--month | -y|--year | -l|--last <dur>]
  atcoder config <show | get <key> | set <key> <value> | unset <key> | path>
  atcoder completion <bash|zsh|fish>
  atcoder commit
  atcoder update [--check | --local]
  atcoder version
  atcoder <alias> [args...]   # config の [alias] (例 alias.upd-lo = "update --local")`)
}
