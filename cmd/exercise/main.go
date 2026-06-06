package main

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"time"
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
	default:
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, `Usage:
  exercise new
  exercise test <contest> --task <task> [--refresh]`)
}

func cmdNew() error {
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
