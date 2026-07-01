package main

import (
	"bufio"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/atcoder"
	"github.com/cry999/atcoder-daily-training/internal/cliargs"
	"golang.org/x/term"
)

// cmdLogin は `atcoder login` を捌く (要件 062)。ブラウザで得た REVEL_SESSION
// cookie を手貼りで取り込み、login-gated ページを 1 回 GET して検証し、
// session.toml (0600) に保存する。`--status` は取り込みをせず保存済み状態を表示する。
func cmdLogin(args []string) (int, error) {
	flagArgs, positionals := cliargs.Split(args)
	fs := flag.NewFlagSet("login", flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	cookieFlag := fs.String("session-cookie", "", "REVEL_SESSION cookie value to import (default: read from stdin)")
	statusFlag := fs.Bool("status", false, "show saved session status without importing (no cookie needed)")
	checkFlag := fs.Bool("check", false, "with --status, re-validate the saved session over the network")
	if err := fs.Parse(flagArgs); err != nil {
		return 2, err
	}
	if len(positionals) > 0 {
		return 2, fmt.Errorf("unexpected argument: %s", positionals[0])
	}
	set := map[string]bool{}
	fs.Visit(func(f *flag.Flag) { set[f.Name] = true })

	if *statusFlag {
		if set["session-cookie"] {
			return 2, errors.New("--status は --session-cookie と併用できません")
		}
		return loginStatus(*checkFlag)
	}
	if *checkFlag {
		return 2, errors.New("--check は --status と併用してください")
	}

	cookie, err := readCookie(*cookieFlag, set["session-cookie"])
	if err != nil {
		return 2, err
	}
	if cookie == "" {
		return 2, errors.New("empty cookie")
	}

	username, err := atcoder.Validate(cookie)
	if err != nil {
		return 1, validateErr(err)
	}
	s := &atcoder.Session{RevelSession: cookie, Username: username, LoggedInAt: time.Now()}
	if err := atcoder.Save(s); err != nil {
		return 1, err
	}
	fmt.Printf("logged in as %s\n", username)
	return 0, nil
}

// loginStatus は保存済みセッションの状態を表示する。--check なら検証 GET を 1 回行う。
func loginStatus(check bool) (int, error) {
	s, err := atcoder.Load()
	if err != nil {
		if errors.Is(err, atcoder.ErrNoSession) {
			fmt.Println("not logged in")
			return 0, nil
		}
		return 1, err
	}
	line := fmt.Sprintf("logged in as %s (since %s)", s.Username, s.LoggedInAt.Format(time.RFC3339))
	if !check {
		fmt.Println(line)
		return 0, nil
	}
	if _, verr := atcoder.Validate(s.RevelSession); verr != nil {
		if errors.Is(verr, atcoder.ErrUnauthenticated) {
			fmt.Printf("%s — expired (please re-login)\n", line)
			return 1, nil
		}
		return 1, validateErr(verr)
	}
	fmt.Printf("%s — valid\n", line)
	return 0, nil
}

// readCookie は取り込む cookie 値を用意する。--session-cookie があればそれを、
// 無ければ stdin から読む (TTY はエコーせず秘匿入力、非 TTY はそのまま 1 行)。
func readCookie(flagVal string, flagSet bool) (string, error) {
	if flagSet {
		return normalizeCookie(flagVal), nil
	}
	if term.IsTerminal(int(os.Stdin.Fd())) {
		fmt.Fprint(os.Stderr, "REVEL_SESSION: ")
		b, err := term.ReadPassword(int(os.Stdin.Fd()))
		fmt.Fprintln(os.Stderr)
		if err != nil {
			return "", err
		}
		return normalizeCookie(string(b)), nil
	}
	line, err := bufio.NewReader(os.Stdin).ReadString('\n')
	if err != nil && err != io.EOF {
		return "", err
	}
	return normalizeCookie(line), nil
}

// normalizeCookie は前後の空白・改行を除去し、`REVEL_SESSION=` 接頭辞が付いていれば剥がす。
func normalizeCookie(s string) string {
	s = strings.TrimSpace(s)
	s = strings.TrimPrefix(s, "REVEL_SESSION=")
	return strings.TrimSpace(s)
}

// validateErr は internal/atcoder の検証エラーを利用者向けメッセージに変換する。
// cookie の生値は一切含めない (秘匿)。
func validateErr(err error) error {
	switch {
	case errors.Is(err, atcoder.ErrUnauthenticated):
		return errors.New("cookie is invalid or expired (log in via browser and copy a fresh REVEL_SESSION)")
	case errors.Is(err, atcoder.ErrChallenge):
		return errors.New("hit Cloudflare challenge; open the browser, refresh, and copy a new REVEL_SESSION")
	default:
		return err
	}
}
