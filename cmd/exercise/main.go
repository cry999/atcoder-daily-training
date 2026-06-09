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
			fmt.Fprintln(os.Stderr, "exercise new:", err)
			os.Exit(1)
		}
	case "test":
		code, err := cmdTest(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "exercise test:", err)
		}
		os.Exit(code)
	case "run":
		code, err := cmdRun(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "exercise run:", err)
		}
		os.Exit(code)
	case "submit":
		code, err := cmdSubmit(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "exercise submit:", err)
		}
		os.Exit(code)
	case "commit":
		code, err := cmdCommit(os.Args[2:])
		if err != nil {
			fmt.Fprintln(os.Stderr, "exercise commit:", err)
		}
		os.Exit(code)
	default:
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, `Usage:
  exercise new
  exercise new abc <contest> [--tasks <list>] [--refresh] [--no-skeleton] [--no-fetch]
  exercise test   <contest> --task <task> [-v] [-d] [-s] [-c <N[,M,...]>] [--refresh] [--timeout <dur>] [--tolerance <eps>] [--layout <auto|abc|exercise>]
  exercise run    <contest> --task <task> [-v] [-d] [--in <path>|-] [--out <path>] [--tolerance <eps>] [--timeout <dur>] [--layout <auto|abc|exercise>]
  exercise submit <contest> --task <task> [--refresh] [--tolerance <eps>] [--no-open] [--layout <auto|abc|exercise>]
  exercise commit`)
}
