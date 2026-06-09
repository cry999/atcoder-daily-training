package atcoder

import (
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"strings"
	"testing"

	"golang.org/x/net/html"
)

// これらは純粋関数 (CSRF 抽出・cookie 取り出し) のみを検証する。
// 実ログイン (Login) はユーザの AtCoder 資格情報とネットワークが必要なため、
// 単体テストでは検証しない (CI/オフラインで落とさない方針)。

// loginFormHTML は GET https://atcoder.jp/login が返すフォームを模した
// 現実的な HTML。隠し csrf_token を含む。
func loginFormHTML(csrf string) string {
	return `<!DOCTYPE html>
<html lang="ja">
<head><meta charset="utf-8"><title>ログイン - AtCoder</title></head>
<body>
  <div class="container">
    <form action="" method="POST">
      <input type="hidden" name="csrf_token" value="` + csrf + `" />
      <div class="form-group">
        <label for="username">ユーザ名</label>
        <input type="text" id="username" name="username" class="form-control" />
      </div>
      <div class="form-group">
        <label for="password">パスワード</label>
        <input type="password" id="password" name="password" class="form-control" />
      </div>
      <button type="submit" class="btn btn-primary">ログイン</button>
    </form>
  </div>
</body>
</html>`
}

func parseHTML(t *testing.T, s string) *html.Node {
	t.Helper()
	doc, err := html.Parse(strings.NewReader(s))
	if err != nil {
		t.Fatalf("html.Parse failed: %v", err)
	}
	return doc
}

func TestExtractCSRF_present(t *testing.T) {
	const want = "GExvLkM7TnGQ9aH3WqZ0pY8sUmRfBvCxDeFgHiJk=="
	doc := parseHTML(t, loginFormHTML(want))
	got, err := extractCSRF(doc)
	if err != nil {
		t.Fatalf("extractCSRF returned error: %v", err)
	}
	if got != want {
		t.Fatalf("csrf_token = %q, want %q", got, want)
	}
}

func TestExtractCSRF_missing(t *testing.T) {
	// csrf_token フィールドを持たないフォーム。
	const noCSRF = `<!DOCTYPE html><html><body>
		<form action="" method="POST">
			<input type="text" name="username" />
			<input type="password" name="password" />
		</form></body></html>`
	doc := parseHTML(t, noCSRF)
	if _, err := extractCSRF(doc); err == nil {
		t.Fatal("extractCSRF: expected error when csrf_token is missing, got nil")
	}
}

func TestExtractCSRF_empty(t *testing.T) {
	// csrf_token は存在するが value が空。
	doc := parseHTML(t, loginFormHTML(""))
	if _, err := extractCSRF(doc); err == nil {
		t.Fatal("extractCSRF: expected error when csrf_token value is empty, got nil")
	}
}

func TestRevelSession_found(t *testing.T) {
	jar, err := cookiejar.New(nil)
	if err != nil {
		t.Fatalf("cookiejar.New: %v", err)
	}
	u, _ := url.Parse(baseURL)
	jar.SetCookies(u, []*http.Cookie{
		{Name: "OTHER", Value: "ignored"},
		{Name: "REVEL_SESSION", Value: "abc123def"},
	})
	got := revelSession(jar)
	const want = "REVEL_SESSION=abc123def"
	if got != want {
		t.Fatalf("revelSession = %q, want %q", got, want)
	}
}

func TestRevelSession_absent(t *testing.T) {
	jar, err := cookiejar.New(nil)
	if err != nil {
		t.Fatalf("cookiejar.New: %v", err)
	}
	u, _ := url.Parse(baseURL)
	jar.SetCookies(u, []*http.Cookie{
		{Name: "OTHER", Value: "x"},
	})
	if got := revelSession(jar); got != "" {
		t.Fatalf("revelSession = %q, want empty string when REVEL_SESSION absent", got)
	}
}
