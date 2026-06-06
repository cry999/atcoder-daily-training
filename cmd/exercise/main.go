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
		if err := cmdNew(); err != nil {
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
	default:
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, `Usage:
  exercise new
  exercise test <contest> --task <task> [-v] [-d] [-c <N[,M,...]>] [--refresh] [--timeout <dur>]
  exercise run  <contest> --task <task> [-v] [-d] [--stdin <path>|-] [--timeout <dur>]`)
}
