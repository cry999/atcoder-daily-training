package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}

	switch os.Args[1] {
	case "new":
		if err := cmdNew(os.Args[2:]); err != nil {
			fmt.Fprintln(os.Stderr, "atcoder new:", err)
			os.Exit(1)
		}
	case "test":
		code, err := cmdTest(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder test:", err)
		}
		os.Exit(code)
	case "login":
		code, err := cmdLogin(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder login:", err)
		}
		os.Exit(code)
	case "logout":
		code, err := cmdLogout(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder logout:", err)
		}
		os.Exit(code)
	case "status":
		code, err := cmdStatus(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder status:", err)
		}
		os.Exit(code)
	case "stats":
		code, err := cmdStats(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder stats:", err)
		}
		os.Exit(code)
	case "config":
		code, err := cmdConfig(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder config:", err)
		}
		os.Exit(code)
	case "commit":
		code, err := cmdCommit(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder commit:", err)
		}
		os.Exit(code)
	case "completion":
		code, err := cmdCompletion(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder completion:", err)
		}
		os.Exit(code)
	case "update":
		code, err := cmdUpdate(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder update:", err)
		}
		os.Exit(code)
	case "version":
		code, err := cmdVersion(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder version:", err)
		}
		os.Exit(code)
	case "__complete":
		// 隠しヘルパ。補完スクリプトからのみ呼ばれる。補完を壊さないため常に exit 0。
		code, _ := cmdComplete(os.Args[2:])
		os.Exit(code)
	default:
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, `Usage:
  atcoder new
  atcoder new abc <contest> [--tasks <list>] [--refresh] [--no-skeleton] [--no-fetch]
  atcoder test   <contest> --task <task>   # default: judge downloaded samples
                 [sample: -c <N[,M,...]> | --refresh | -j <n> | -w | -s | --submit [--no-open]]
                 [ad-hoc: --in <path>|- | --out <path> | --interactive]
                 [-v] [-d] [--timeout <dur>] [--tolerance <eps>] [--layout <auto|abc|exercise>]
  atcoder login  [--user <name>] [--password-stdin]
  atcoder logout
  atcoder status <contest> [--task <task>] [-w|--watch] [--interval <dur>] [--open]
  atcoder stats  [-w|--week | -m|--month | -y|--year | -l|--last <dur>] [-g|--graph]
  atcoder config <show | get <key> | set <key> <value> | path>
  atcoder completion <bash|zsh|fish>
  atcoder commit
  atcoder update [--check]
  atcoder version`)
}
