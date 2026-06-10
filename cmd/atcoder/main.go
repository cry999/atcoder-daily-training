package main

import (
	"fmt"
	"os"

	"github.com/cry999/atcoder-daily-training/internal/alias"
	"github.com/cry999/atcoder-daily-training/internal/config"
)

// builtins は組み込みサブコマンド名の集合。下の switch・usage() と同期させること。
// alias より常に優先される (alias は未知名のときだけ解決される)。
var builtins = map[string]bool{
	"new": true, "start": true, "test": true, "stats": true, "review": true,
	"config": true, "commit": true, "completion": true,
	"update": true, "version": true, "__complete": true,
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

	switch args[0] {
	case "new":
		if err := cmdNew(args[1:]); err != nil {
			fmt.Fprintln(os.Stderr, "atcoder new:", err)
			os.Exit(1)
		}
	case "start":
		code, err := cmdStart(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder start:", err)
		}
		os.Exit(code)
	case "test":
		code, err := cmdTest(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder test:", err)
		}
		os.Exit(code)
	case "stats":
		code, err := cmdStats(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder stats:", err)
		}
		os.Exit(code)
	case "review":
		code, err := cmdReview(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder review:", err)
		}
		os.Exit(code)
	case "config":
		code, err := cmdConfig(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder config:", err)
		}
		os.Exit(code)
	case "commit":
		code, err := cmdCommit(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder commit:", err)
		}
		os.Exit(code)
	case "completion":
		code, err := cmdCompletion(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder completion:", err)
		}
		os.Exit(code)
	case "update":
		code, err := cmdUpdate(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder update:", err)
		}
		os.Exit(code)
	case "version":
		code, err := cmdVersion(args[1:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder version:", err)
		}
		os.Exit(code)
	case "__complete":
		// 隠しヘルパ。補完スクリプトからのみ呼ばれる。補完を壊さないため常に exit 0。
		code, _ := cmdComplete(args[1:])
		os.Exit(code)
	default:
		usage()
		os.Exit(2)
	}
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
                 [sample: -c <N[,M,...]> | --refresh | -j <n> | -w | -s | --submit [--no-open]]
                 [ad-hoc: --in <path>|- | --out <path> | --interactive]
                 [-v] [-d] [--timeout <dur>] [--tolerance <eps>] [--layout <auto|abc|exercise>]
  atcoder stats  [-w|--week | -m|--month | -y|--year | -l|--last <dur>] [-g|--graph]
  atcoder review <category> [-w|--week | -m|--month | -y|--year | -l|--last <dur>]
  atcoder config <show | get <key> | set <key> <value> | unset <key> | path>
  atcoder completion <bash|zsh|fish>
  atcoder commit
  atcoder update [--check | --local]
  atcoder version
  atcoder <alias> [args...]   # config の [alias] (例 alias.upd-lo = "update --local")`)
}
