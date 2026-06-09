package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/atcoder"
	"golang.org/x/term"
)

// cmdLogin は AtCoder のセッション cookie (REVEL_SESSION) を取り込んで保存する。
//
// AtCoder のログインページは Cloudflare Turnstile で保護されており、username/
// password の programmatic ログインはできない。そこでブラウザでログイン
// (Turnstile はブラウザが解決) し、その REVEL_SESSION cookie を貼り付けてもらう。
// 既定は対話プロンプト。非対話には --session-cookie / --session-stdin。
func cmdLogin(args []string) (int, error) {
	flags := flag.NewFlagSet("login", flag.ContinueOnError)
	userFlag := flags.String("user", "", "AtCoder username (省略時はセッションから自動取得)")
	cookieFlag := flags.String("session-cookie", "", "REVEL_SESSION の値を直接指定 (ps/シェル履歴に残る点に注意)")
	cookieStdin := flags.Bool("session-stdin", false, "REVEL_SESSION の値を stdin から読む (非対話)")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args); err != nil {
		return 2, err
	}

	raw, code, err := readCookie(*cookieFlag, *cookieStdin)
	if err != nil {
		return code, err
	}
	raw = sanitizeSecret(raw)
	if raw == "" {
		return 2, errors.New("セッション cookie が空です")
	}

	sess, err := atcoder.SessionFromCookie(raw, *userFlag)
	if err != nil {
		return 1, err
	}
	if err := atcoder.SaveSession(sess); err != nil {
		return 1, err
	}
	if sess.User != "" {
		fmt.Printf("ログインしました: %s\n", sess.User)
	} else {
		fmt.Println("ログインしました (セッション cookie を保存しました)")
	}
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

// readCookie は REVEL_SESSION の値を取得する。優先順位は --session-cookie >
// --session-stdin > 対話プロンプト。戻り値は (値, exit code, err)。
func readCookie(flagVal string, stdin bool) (string, int, error) {
	if flagVal != "" {
		return flagVal, 0, nil
	}
	if stdin {
		b, err := io.ReadAll(os.Stdin)
		if err != nil {
			return "", 1, err
		}
		return strings.TrimSpace(string(b)), 0, nil
	}
	if !term.IsTerminal(int(os.Stdin.Fd())) {
		return "", 2, errors.New("対話入力には端末が必要です (非対話なら --session-cookie か --session-stdin)")
	}
	printCookieInstructions()
	fmt.Fprint(os.Stderr, "REVEL_SESSION の値を貼り付け: ")
	// cookie は認証トークンなので非表示で受ける。
	b, err := term.ReadPassword(int(os.Stdin.Fd()))
	fmt.Fprintln(os.Stderr)
	if err != nil {
		return "", 1, err
	}
	return string(b), 0, nil
}

func printCookieInstructions() {
	fmt.Fprintln(os.Stderr, `AtCoder のログインは Cloudflare Turnstile で保護されているため、ブラウザの
セッション cookie を取り込みます。手順:
  1. ブラウザで https://atcoder.jp にログインする
  2. DevTools を開く (F12) → Application/ストレージ → Cookies → https://atcoder.jp
  3. 名前 "REVEL_SESSION" の値をコピーする
  4. 下に貼り付けて Enter (入力は表示されません)`)
}

// sanitizeSecret は端末のブラケットペースト (\x1b[200~ … \x1b[201~) のラッパや
// 紛れ込んだ制御文字を除去し、前後の空白を落とす。これらは端末由来で値の一部
// ではない。通常の文字 (記号含む) は変更しない。
func sanitizeSecret(s string) string {
	s = strings.ReplaceAll(s, "\x1b[200~", "")
	s = strings.ReplaceAll(s, "\x1b[201~", "")
	s = strings.Map(func(r rune) rune {
		if r == '\t' {
			return r
		}
		if r < 0x20 || r == 0x7f {
			return -1
		}
		return r
	}, s)
	return strings.TrimSpace(s)
}
