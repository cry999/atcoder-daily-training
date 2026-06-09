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
	showPw := flags.Bool("show-password", false, "パスワードを画面に表示しながら入力する (デバッグ用)")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args); err != nil {
		return 2, err
	}

	user := *userFlag
	password, err := readPassword(*pwStdin, *showPw, &user)
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

// errNeedUser は --password-stdin 指定時に --user が無いことを表す (exit 2)。
var errNeedUser = errors.New("--password-stdin 時は --user が必要です")

// passwordErrCode は readPassword のエラーを exit code に写す。利用方法の誤り
// (端末が無い / --user 不足) は引数エラー扱いで 2、それ以外は 1。
func passwordErrCode(err error) int {
	if errors.Is(err, errNeedTTY) || errors.Is(err, errNeedUser) {
		return 2
	}
	return 1
}

// readPassword はユーザ名 (未指定なら対話で補完) とパスワードを取得する。
// --password-stdin 時は stdin からパスワードを読み、ユーザ名は --user 必須。
// showPw 時は端末からパスワードを表示しながら読み、入力値を確認表示する (デバッグ用)。
// いずれの経路でも端末のブラケットペースト由来の制御列を除去し、ATCODER_DEBUG
// または showPw 時は受け取ったバイト列を hex で確認表示する。
func readPassword(pwStdin, showPw bool, user *string) (string, error) {
	raw, err := readRawPassword(pwStdin, showPw, user)
	if err != nil {
		return "", err
	}

	pw := sanitizePassword(raw)
	if os.Getenv("ATCODER_DEBUG") != "" || showPw {
		fmt.Fprintf(os.Stderr, "[debug] user=%q password=%q (len=%d)\n", *user, pw, len(pw))
		fmt.Fprintf(os.Stderr, "[debug] password bytes (hex): % x\n", []byte(raw))
		if pw != raw {
			fmt.Fprintln(os.Stderr, "[debug] ※ ブラケットペースト/制御列を除去しました (端末由来でパスワードの一部ではありません)")
		}
	}
	return pw, nil
}

// readRawPassword は加工前のパスワード文字列を読む。
func readRawPassword(pwStdin, showPw bool, user *string) (string, error) {
	if pwStdin {
		if *user == "" {
			return "", errNeedUser
		}
		b, err := io.ReadAll(os.Stdin)
		if err != nil {
			return "", err
		}
		return strings.TrimRight(string(b), "\r\n"), nil
	}

	// 対話入力。ユーザ名が未指定ならまず尋ねる (show/非 show 共通の scanner)。
	sc := bufio.NewScanner(os.Stdin)
	if *user == "" {
		if !term.IsTerminal(int(os.Stdin.Fd())) {
			return "", errNeedTTY
		}
		fmt.Fprint(os.Stderr, "Username: ")
		if sc.Scan() {
			*user = strings.TrimSpace(sc.Text())
		}
	}

	if !term.IsTerminal(int(os.Stdin.Fd())) {
		return "", errNeedTTY
	}

	if showPw {
		// デバッグ用: パスワードを画面に表示しながら入力する。
		fmt.Fprint(os.Stderr, "Password (※画面に表示されます): ")
		if sc.Scan() {
			return sc.Text(), nil
		}
		return "", nil
	}

	fmt.Fprint(os.Stderr, "Password: ")
	b, err := term.ReadPassword(int(os.Stdin.Fd()))
	fmt.Fprintln(os.Stderr)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

// sanitizePassword は端末のブラケットペースト (\x1b[200~ … \x1b[201~) のラッパや、
// 紛れ込んだ ESC 制御列を除去する。これらは端末由来でパスワードの一部ではなく、
// 含まれていると AtCoder 認証が「資格情報誤り」で弾かれる。通常のパスワード文字
// (記号含む) は一切変更しない。
func sanitizePassword(s string) string {
	// ブラケットペーストのラッパを除去。
	s = strings.ReplaceAll(s, "\x1b[200~", "")
	s = strings.ReplaceAll(s, "\x1b[201~", "")
	// 念のため残った C0 制御文字 (TAB を除く) を除去。印字可能文字のみ残す。
	s = strings.Map(func(r rune) rune {
		if r == '\t' {
			return r
		}
		if r < 0x20 || r == 0x7f {
			return -1
		}
		return r
	}, s)
	return s
}
