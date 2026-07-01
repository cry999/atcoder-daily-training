package testexec

import (
	"errors"
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

	_, err := fetchProblem(srv.URL + "/contests/abc457/tasks/abc457_a")
	if err == nil {
		t.Fatal("fetchProblem returned nil error for HTTP 404, want error")
	}
	// 非 200 は型付きエラー (httpStatusError) で、ステータスを識別できること。
	// resolveAndFetch の 404 フォールバック判定がこれに依存する。
	var se *httpStatusError
	if !errors.As(err, &se) {
		t.Fatalf("error is not *httpStatusError: %v", err)
	}
	if se.Code != http.StatusNotFound {
		t.Errorf("status code = %d, want 404", se.Code)
	}
}

// resolveAndFetch の 404 フォールバック (要件 065) を httptest で固定する。
// 機械生成 URL (abc111_d) は 404、タスク一覧ページと実 task ページ (arc103_b) は
// 200 を配り、override 無しでも実 URL に辿り着くことを検証する。
func TestResolveAndFetchFallbackFromTasksList(t *testing.T) {
	tasksPage, err := os.ReadFile("testdata/tasks_abc111.html")
	if err != nil {
		t.Fatalf("read tasks testdata: %v", err)
	}
	problemPage, err := os.ReadFile("testdata/problem_abc457_a.html")
	if err != nil {
		t.Fatalf("read problem testdata: %v", err)
	}

	var hits []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hits = append(hits, r.URL.Path)
		switch r.URL.Path {
		case "/contests/abc111/tasks/abc111_d":
			// 機械生成 (推定 task_id) URL は存在しない。
			http.Error(w, "not found", http.StatusNotFound)
		case "/contests/abc111/tasks":
			w.Header().Set("Content-Type", "text/html; charset=utf-8")
			w.Write(tasksPage)
		case "/contests/abc111/tasks/arc103_b":
			// 一覧ページから解決される実 task ページ。
			w.Header().Set("Content-Type", "text/html; charset=utf-8")
			w.Write(problemPage)
		default:
			http.Error(w, "unexpected path "+r.URL.Path, http.StatusInternalServerError)
		}
	}))
	defer srv.Close()

	old := baseURL
	baseURL = srv.URL
	t.Cleanup(func() { baseURL = old })

	// override 無しで abc111 の D (letter d, index 3 → arc103_b) を取得する。
	prob, err := resolveAndFetch("abc111", "abc111_d", "")
	if err != nil {
		t.Fatalf("resolveAndFetch: %v", err)
	}
	wantURL := srv.URL + "/contests/abc111/tasks/arc103_b"
	if prob.URL != wantURL {
		t.Errorf("resolved URL = %q, want %q", prob.URL, wantURL)
	}
	if len(prob.Samples) == 0 {
		t.Error("no samples fetched from the resolved URL")
	}

	// フォールバックの各段が正しい順で呼ばれていること: 機械生成 404 → 一覧ページ →
	// 実 task ページ。
	wantHits := []string{
		"/contests/abc111/tasks/abc111_d",
		"/contests/abc111/tasks",
		"/contests/abc111/tasks/arc103_b",
	}
	if len(hits) != len(wantHits) {
		t.Fatalf("hits = %v, want %v", hits, wantHits)
	}
	for i, h := range wantHits {
		if hits[i] != h {
			t.Errorf("hits[%d] = %q, want %q", i, hits[i], h)
		}
	}
}

// override が設定されているときは 404 でもフォールバックせず、そのエラーを表面化する
// (人が明示した URL の 404 を握り潰さない)。要件 065 のエラーハンドリング。
func TestResolveAndFetchNoFallbackWithOverride(t *testing.T) {
	var hits []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hits = append(hits, r.URL.Path)
		http.Error(w, "not found", http.StatusNotFound)
	}))
	defer srv.Close()

	old := baseURL
	baseURL = srv.URL
	t.Cleanup(func() { baseURL = old })

	override := srv.URL + "/contests/abc111/tasks/some_task"
	if _, err := resolveAndFetch("abc111", "abc111_d", override); err == nil {
		t.Fatal("resolveAndFetch returned nil error for 404 override, want error")
	}
	// override の 1 リクエストのみ。一覧ページ (/contests/abc111/tasks) は引かない。
	for _, h := range hits {
		if h == "/contests/abc111/tasks" {
			t.Errorf("tasks list page was fetched despite override: hits=%v", hits)
		}
	}
}
