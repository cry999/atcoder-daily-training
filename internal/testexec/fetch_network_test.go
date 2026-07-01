package testexec

import (
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
)

// fetchProblem の HTTP 取得〜HTML 解析の結線を、testdata に保存した実ページ相当の
// HTML を httptest で配って検証する (実 AtCoder には触れない)。ここが従来テストの
// 穴で、extractSamples 等の解析関数は単体テストされていたが、?lang=ja 付与や
// ステータス判定を含む fetchProblem 本体は無検証だった。
func TestFetchProblemFromTestdata(t *testing.T) {
	page, err := os.ReadFile("testdata/problem_abc457_a.html")
	if err != nil {
		t.Fatalf("read testdata: %v", err)
	}

	var gotQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotQuery = r.URL.RawQuery
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write(page)
	}))
	defer srv.Close()

	prob, err := fetchProblem(srv.URL + "/contests/abc457/tasks/abc457_a")
	if err != nil {
		t.Fatalf("fetchProblem: %v", err)
	}

	// fetchProblem は日本語ページを引くため ?lang=ja を必ず付ける。
	if gotQuery != "lang=ja" {
		t.Errorf("query = %q, want %q", gotQuery, "lang=ja")
	}
	if prob.TimeLimitMs != 2000 {
		t.Errorf("TimeLimitMs = %d, want 2000", prob.TimeLimitMs)
	}

	if len(prob.Samples) != 2 {
		t.Fatalf("len(Samples) = %d, want 2", len(prob.Samples))
	}
	wantSamples := []sample{
		{Input: "2 3\n", Output: "5\n"},
		{Input: "100 100\n", Output: "200\n"},
	}
	for i, w := range wantSamples {
		if prob.Samples[i] != w {
			t.Errorf("Samples[%d] = %+v, want %+v", i, prob.Samples[i], w)
		}
	}

	// 入力形式節の <pre> がベストエフォートで取れていること (要件 060)。
	if prob.InputFormat != "A B" {
		t.Errorf("InputFormat = %q, want %q", prob.InputFormat, "A B")
	}
	// 制約節のテキストがベストエフォートで取れていること。
	if prob.Constraints == "" {
		t.Error("Constraints is empty, want non-empty")
	}
}

// 200 以外はエラーにする (存在しない問題や rate limit のとき、無言でキャッシュを
// 壊さないため)。fetchProblem が HTTP ステータスを見ていることを固定する。
func TestFetchProblemNon200(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "not found", http.StatusNotFound)
	}))
	defer srv.Close()

	if _, err := fetchProblem(srv.URL + "/contests/abc457/tasks/abc457_a"); err == nil {
		t.Fatal("fetchProblem returned nil error for HTTP 404, want error")
	}
}
