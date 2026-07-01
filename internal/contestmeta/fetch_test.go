package contestmeta

import (
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"
)

// testdata の実ページ相当 HTML を配る httptest サーバを立て、baseURL をそこへ
// 向け替えて Fetch を丸ごと検証する。従来 contestmeta にはテストが無く、トップ +
// タスク一覧の 2 ページ取得〜Meta 組み立ての結線が無検証だった。実 AtCoder には触れない。
func newContestServer(t *testing.T) *httptest.Server {
	t.Helper()
	top, err := os.ReadFile("testdata/contest_top.html")
	if err != nil {
		t.Fatalf("read top testdata: %v", err)
	}
	tasks, err := os.ReadFile("testdata/contest_tasks.html")
	if err != nil {
		t.Fatalf("read tasks testdata: %v", err)
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/contests/abc457/tasks", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write(tasks)
	})
	mux.HandleFunc("/contests/abc457", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write(top)
	})
	return httptest.NewServer(mux)
}

func TestFetchFromTestdata(t *testing.T) {
	srv := newContestServer(t)
	defer srv.Close()

	old := baseURL
	baseURL = srv.URL
	t.Cleanup(func() { baseURL = old })

	meta, err := Fetch("abc457")
	if err != nil {
		t.Fatalf("Fetch: %v", err)
	}

	if meta.Contest != "abc457" {
		t.Errorf("Contest = %q, want %q", meta.Contest, "abc457")
	}
	if meta.Title != "AtCoder Beginner Contest 457" {
		t.Errorf("Title = %q, want %q", meta.Title, "AtCoder Beginner Contest 457")
	}

	wantTasks := []string{"abc457_a", "abc457_b", "abc457_c", "abc457_d"}
	if len(meta.Tasks) != len(wantTasks) {
		t.Fatalf("Tasks = %v, want %v", meta.Tasks, wantTasks)
	}
	for i, w := range wantTasks {
		if meta.Tasks[i] != w {
			t.Errorf("Tasks[%d] = %q, want %q", i, meta.Tasks[i], w)
		}
	}

	// 開始/終了時刻とその差 (100 分) が取れていること。
	if meta.StartAt.IsZero() || meta.EndAt.IsZero() {
		t.Fatalf("StartAt/EndAt not parsed: start=%v end=%v", meta.StartAt, meta.EndAt)
	}
	if got, want := meta.DurationMs, int(100*time.Minute/time.Millisecond); got != want {
		t.Errorf("DurationMs = %d, want %d", got, want)
	}
}

// タスクが 1 つも取れなければエラーにする (URL 誤り等で空 Meta をキャッシュしないため)。
func TestFetchNoTasks(t *testing.T) {
	top, err := os.ReadFile("testdata/contest_top.html")
	if err != nil {
		t.Fatalf("read top testdata: %v", err)
	}
	mux := http.NewServeMux()
	// タスク一覧は該当リンクを含まない空テーブルを返す。
	mux.HandleFunc("/contests/abc457/tasks", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte(`<html><body><table></table></body></html>`))
	})
	mux.HandleFunc("/contests/abc457", func(w http.ResponseWriter, r *http.Request) {
		w.Write(top)
	})
	srv := httptest.NewServer(mux)
	defer srv.Close()

	old := baseURL
	baseURL = srv.URL
	t.Cleanup(func() { baseURL = old })

	if _, err := Fetch("abc457"); err == nil {
		t.Fatal("Fetch returned nil error for empty task list, want error")
	}
}

// 200 以外はエラーにする。fetchDoc が HTTP ステータスを見ていることを固定する。
func TestFetchDocNon200(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "boom", http.StatusServiceUnavailable)
	}))
	defer srv.Close()

	if _, err := fetchDoc(srv.URL + "/contests/abc457"); err == nil {
		t.Fatal("fetchDoc returned nil error for HTTP 503, want error")
	}
}
