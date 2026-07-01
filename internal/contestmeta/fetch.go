package contestmeta

import (
	"fmt"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/antchfx/htmlquery"
	"golang.org/x/net/html"
)

const userAgent = "atcoder-test/0.1 (+https://github.com/cry999/atcoder-daily-training)"

// baseURL は取得元オリジン。本番は AtCoder 固定だが、テストが httptest サーバへ
// 向け替えできるよう変数にしている (実ネットワークを踏まずに Fetch を結線検証する)。
var baseURL = "https://atcoder.jp"

// fixtime のフォーマット例: "2024-06-15 21:00:00+0900"
const fixtimeLayout = "2006-01-02 15:04:05-0700"

// Fetch は contest トップページとタスク一覧ページを取得し、Meta を組み立てる。
// 開始 / 終了時刻が取れなくても、タスクリストが取れていれば成功扱いとする
// (時刻はゼロ値のまま。サンプル取得を妨げないための割り切り)。
func Fetch(contest string) (*Meta, error) {
	base := baseURL + "/contests/" + contest

	topDoc, err := fetchDoc(base)
	if err != nil {
		return nil, fmt.Errorf("contest top page: %w", err)
	}
	tasksDoc, err := fetchDoc(base + "/tasks")
	if err != nil {
		return nil, fmt.Errorf("tasks page: %w", err)
	}

	tasks := extractTasks(tasksDoc, contest)
	if len(tasks) == 0 {
		return nil, fmt.Errorf("no tasks found for %s", contest)
	}

	start, end := extractTimes(topDoc)
	durationMs := 0
	if !start.IsZero() && !end.IsZero() {
		durationMs = int(end.Sub(start) / time.Millisecond)
	}

	return &Meta{
		Contest:    contest,
		URL:        base,
		Title:      extractTitle(topDoc),
		StartAt:    start,
		EndAt:      end,
		DurationMs: durationMs,
		Tasks:      tasks,
		FetchedAt:  time.Now(),
	}, nil
}

func fetchDoc(url string) (*html.Node, error) {
	req, err := http.NewRequest("GET", url+"?lang=ja", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept-Language", "ja,en-US;q=0.9,en;q=0.8")
	req.Header.Set("User-Agent", userAgent)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("HTTP request failed: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP %d for %s", resp.StatusCode, url)
	}
	return htmlquery.Parse(resp.Body)
}

// extractTitle は contest トップページからコンテスト名を取り出す。
func extractTitle(doc *html.Node) string {
	if a := htmlquery.FindOne(doc, `//a[contains(@class,"contest-title")]`); a != nil {
		if t := strings.TrimSpace(htmlquery.InnerText(a)); t != "" {
			return t
		}
	}
	// fallback: <title>AtCoder Beginner Contest 457 - AtCoder</title>
	if t := htmlquery.FindOne(doc, `//title`); t != nil {
		s := strings.TrimSpace(htmlquery.InnerText(t))
		if i := strings.LastIndex(s, " - "); i > 0 {
			s = s[:i]
		}
		return strings.TrimSpace(s)
	}
	return ""
}

// extractTimes は <small class="contest-duration"> 内の <time class="fixtime">
// 2 要素 (開始 / 終了) をパースする。取れない要素はゼロ値で返す。
func extractTimes(doc *html.Node) (start, end time.Time) {
	nodes := htmlquery.Find(doc, `//*[contains(@class,"contest-duration")]//time[contains(@class,"fixtime")]`)
	if len(nodes) >= 1 {
		start = parseFixtime(htmlquery.InnerText(nodes[0]))
	}
	if len(nodes) >= 2 {
		end = parseFixtime(htmlquery.InnerText(nodes[1]))
	}
	return start, end
}

func parseFixtime(s string) time.Time {
	t, err := time.Parse(fixtimeLayout, strings.TrimSpace(s))
	if err != nil {
		return time.Time{}
	}
	return t
}

// extractTasks は /contests/<contest>/tasks ページから task ID を出現順に集める。
// 各タスク行には同じ task への <a> が複数あるため、重複は除いて順序を保つ。
func extractTasks(doc *html.Node, contest string) []string {
	re := regexp.MustCompile(`^/contests/` + regexp.QuoteMeta(contest) + `/tasks/([^/?#]+)$`)
	seen := make(map[string]bool)
	var tasks []string
	for _, a := range htmlquery.Find(doc, `//a`) {
		m := re.FindStringSubmatch(htmlquery.SelectAttr(a, "href"))
		if m == nil {
			continue
		}
		id := m[1]
		if seen[id] {
			continue
		}
		seen[id] = true
		tasks = append(tasks, id)
	}
	return tasks
}
