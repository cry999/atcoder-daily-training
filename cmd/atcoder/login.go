package main

import (
	"bufio"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/atcoder"
	"golang.org/x/term"
)

// cmdLogin は AtCoder にログインしてセッション cookie を保存する。
// パスワードは保存せず、端末からの非表示入力か --password-stdin で受け取る。
func cmdLogin(args []string) (int, error) {
	flags := flag.NewFlagSet("login", flag.ContinueOnError)
	userFlag := flags.String("user", "", "AtCoder username (省略時は対話入力)")
	pwStdin := flags.Bool("password-stdin", false, "パスワードを stdin から読む (非対話)")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args); err != nil {
		return 2, err
	}

	user := *userFlag
	password, err := readPassword(*pwStdin, &user)
	if err != nil {
		return passwordErrCode(err), err
	}
	if user == "" {
		return 2, errors.New("ユーザ名が空です")
	}
	if password == "" {
		return 2, errors.New("パスワードが空です")
	}

	sess, err := atcoder.Login(user, password)
	if err != nil {
		return 1, err
	}
	if err := atcoder.SaveSession(sess); err != nil {
		return 1, err
	}
	fmt.Printf("ログインしました: %s\n", sess.User)
	return 0, nil
}

// cmdLogout は保存済みセッションを削除する。
func cmdLogout(args []string) (int, error) {
	flags := flag.NewFlagSet("logout", flag.ContinueOnError)
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args); err != nil {
		return 2, err
	}
	if err := atcoder.DeleteSession(); err != nil {
		return 1, err
	}
	fmt.Println("ログアウトしました")
	return 0, nil
}

// errNeedTTY は非表示入力に端末が必要なのに非 TTY だったことを表す (exit 2)。
var errNeedTTY = errors.New("パスワード入力には端末が必要です (非対話なら --password-stdin を使ってください)")

func passwordErrCode(err error) int {
	if errors.Is(err, errNeedTTY) {
		return 2
	}
	return 1
}

// readPassword はユーザ名 (未指定なら対話で補完) とパスワードを取得する。
// --password-stdin 時は stdin からパスワードを読み、ユーザ名は --user 必須。
func readPassword(pwStdin bool, user *string) (string, error) {
	if pwStdin {
		if *user == "" {
			return "", errors.New("--password-stdin 時は --user が必要です")
		}
		b, err := io.ReadAll(os.Stdin)
		if err != nil {
			return "", err
		}
		return strings.TrimRight(string(b), "\r\n"), nil
	}

	// 対話入力。ユーザ名が未指定ならまず尋ねる。
	if *user == "" {
		if !term.IsTerminal(int(os.Stdin.Fd())) {
			return "", errNeedTTY
		}
		fmt.Fprint(os.Stderr, "Username: ")
		sc := bufio.NewScanner(os.Stdin)
		if sc.Scan() {
			*user = strings.TrimSpace(sc.Text())
		}
	}
	if !term.IsTerminal(int(os.Stdin.Fd())) {
		return "", errNeedTTY
	}
	fmt.Fprint(os.Stderr, "Password: ")
	b, err := term.ReadPassword(int(os.Stdin.Fd()))
	fmt.Fprintln(os.Stderr)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
