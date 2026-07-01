package main

import (
	"errors"
	"flag"
	"fmt"
	"os"

	"github.com/cry999/atcoder-daily-training/internal/atcoder"
	"github.com/cry999/atcoder-daily-training/internal/cliargs"
)

// cmdLogout は `atcoder logout` を捌く (要件 062)。保存済み session.toml を削除する。
// 無セッションでも `not logged in` を出して exit 0 (冪等)。ネットワーク不要。
func cmdLogout(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	fs := flag.NewFlagSet("logout", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}
	if len(positionals) > 0 {
		return 2, fmt.Errorf("unexpected argument: %s", positionals[0])
	}

	if _, err := atcoder.Load(); errors.Is(err, atcoder.ErrNoSession) {
		fmt.Println("not logged in")
		return 0, nil
	}
	if err := atcoder.Clear(); err != nil {
		return 1, err
	}
	fmt.Println("logged out")
	return 0, nil
}
