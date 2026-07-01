package testexec

import (
	"errors"
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/antchfx/htmlquery"
	"github.com/cry999/atcoder-daily-training/internal/contestmeta"
	"golang.org/x/net/html"
)

// baseURL は取得元オリジン。本番は AtCoder 固定だが、テストが httptest サーバへ
// 向け替えできるよう変数にしている (実ネットワークを踏まずに fetch を結線検証する)。
var baseURL = "https://atcoder.jp"

type sample struct {
	Input  string
	Output string
}

type problem struct {
	URL         string
	TimeLimitMs int
	Samples     []sample
	// 入力生成 (要件 060) 用に抽出する生セクション。取れなくても空文字で、
	// サンプル取得は妨げない (ベストエフォート)。
	InputFormat string
	Constraints string
}

// DefaultTaskURL は contest/task から標準の問題ページ URL を組み立てる。
// 通常は `/contests/<contest>/tasks/<contest>_<letter>` だが、task_id が
// contest と食い違う問題 (例: abc111 の D = arc103_b) では URL を導出できないので、
// その場合は meta.toml の url override (`atcoder meta set --url`) を使う。
func DefaultTaskURL(contest, task string) string {
	return fmt.Sprintf("%s/contests/%s/tasks/%s", baseURL, contest, task)
}

// resolveFetchURL は取得元 URL を決める。override (meta.toml の url) が空でなければ
// それを優先し、空なら contest/task から導出する。
func resolveFetchURL(contest, task, override string) string {
	if override != "" {
		return override
	}
	return DefaultTaskURL(contest, task)
}

// httpStatusError は fetch 先が 200 以外を返したことを表す型付きエラー。
// 呼び出し側 (resolveAndFetch) が 404 を識別してフォールバックを起動するために使う。
type httpStatusError struct {
	Code int
	URL  string
}

func (e *httpStatusError) Error() string {
	return fmt.Sprintf("HTTP %d for %s", e.Code, e.URL)
}

// resolveAndFetch は override → 機械生成 URL → (404 なら) タスク一覧ページ解決、の順で
// 問題ページを取得する (要件 065)。override があればそれを尊重し、無い場合に機械生成
// URL が 404 のときだけ一覧ページから実 task_id を解決して再取得する。返す
// problem.URL は実際に取得できた URL なので、呼び出し側はそれを meta.toml に記録すれば
// 次回以降は override 経路で直行できる。
func resolveAndFetch(contest, task, override string) (*problem, error) {
	url := resolveFetchURL(contest, task, override)
	prob, err := fetchProblem(url)
	if err == nil {
		return prob, nil
	}
	// override があるとき (人が明示した URL) や 404 以外は、そのままエラーを返す。
	var se *httpStatusError
	if override != "" || !errors.As(err, &se) || se.Code != http.StatusNotFound {
		return nil, err
	}
	// 機械生成 URL が 404。task_id が contest と食い違う共催問題の可能性が高いので、
	// タスク一覧ページから該当 letter の実 task_id を引いて再取得する。解決できなければ
	// 元の 404 を覆い隠さずそのまま返す。
	realURL, ok := resolveURLFromTasksList(contest, task)
	if !ok {
		return nil, err
	}
	return fetchProblem(realURL)
}

// resolveURLFromTasksList は task (= <contest>_<letter>) の letter 位置を使って
// タスク一覧ページから実 task_id を引き、その URL を返す。解決できなければ ok=false。
func resolveURLFromTasksList(contest, task string) (string, bool) {
	idx, ok := letterIndex(task)
	if !ok {
		return "", false
	}
	tasks, err := fetchTaskIDs(contest)
	if err != nil || idx >= len(tasks) {
		return "", false
	}
	real := tasks[idx]
	// 推定 task_id と同じなら別 URL にならない (既に 404 だった)。解決失敗扱い。
	if real == task {
		return "", false
	}
	return DefaultTaskURL(contest, real), true
}

// fetchTaskIDs はタスク一覧ページ (/contests/<contest>/tasks) を取得し、出現順
// (= letter 順) の task_id 配列を返す。取得は testexec の baseURL を使う (fetchProblem
// と同じオリジンなので httptest で一括して差し替えられる)。パースは一覧ページの
// リンク書式を集約している contestmeta.ExtractTaskIDs に委譲する。
func fetchTaskIDs(contest string) ([]string, error) {
	url := baseURL + "/contests/" + contest + "/tasks"
	req, err := http.NewRequest("GET", url+"?lang=ja", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept-Language", "ja,en-US;q=0.9,en;q=0.8")
	req.Header.Set("User-Agent", "atcoder-test/0.1 (+https://github.com/cry999/atcoder-daily-training)")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, &httpStatusError{Code: resp.StatusCode, URL: url}
	}
	doc, err := htmlquery.Parse(resp.Body)
	if err != nil {
		return nil, err
	}
	return contestmeta.ExtractTaskIDs(doc, contest), nil
}

// letterIndex は <contest>_<letter> 形式の末尾 letter を 0 始まりの序数に変換する。
// letter が単一の英小文字 (a–z) でなければ ok=false (index 解決を諦める)。
func letterIndex(task string) (int, bool) {
	i := strings.LastIndex(task, "_")
	if i < 0 {
		return 0, false
	}
	letter := task[i+1:]
	if len(letter) != 1 || letter[0] < 'a' || letter[0] > 'z' {
		return 0, false
	}
	return int(letter[0] - 'a'), true
}

func fetchProblem(url string) (*problem, error) {
	req, err := http.NewRequest("GET", url+"?lang=ja", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept-Language", "ja,en-US;q=0.9,en;q=0.8")
	req.Header.Set("User-Agent", "atcoder-test/0.1 (+https://github.com/cry999/atcoder-daily-training)")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("HTTP request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, &httpStatusError{Code: resp.StatusCode, URL: url}
	}

	doc, err := htmlquery.Parse(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("HTML parse failed: %w", err)
	}

	tlMs, err := extractTimeLimit(doc)
	if err != nil {
		return nil, fmt.Errorf("time limit extract: %w", err)
	}

	samples, err := extractSamples(doc)
	if err != nil {
		return nil, fmt.Errorf("samples extract: %w", err)
	}

	// 入力生成用の生セクション (制約 / 入力形式) をベストエフォートで抽出する。
	// 見つからなくてもエラーにしない (サンプル取得を妨げない)。
	inputFmt, constraints := extractGenSections(doc)

	return &problem{
		URL:         url,
		TimeLimitMs: tlMs,
		Samples:     samples,
		InputFormat: inputFmt,
		Constraints: constraints,
	}, nil
}

var (
	// 節見出しの判定。入力例 (Sample Input) と区別するため "入力" 単独に限定する。
	inputHeadingRe      = regexp.MustCompile(`^(入力|Input)\s*$`)
	constraintHeadingRe = regexp.MustCompile(`^(制約|Constraints)\s*$`)
)

// extractGenSections は問題文の「入力形式」節の <pre> と「制約」節のテキストを
// 生のまま取り出す (要件 060 / ADR 0008)。lang-ja を優先し、無ければ lang-en。
// どちらの節も見つからなければ空文字を返す (呼び出し側でベストエフォート扱い)。
func extractGenSections(doc *html.Node) (inputFormat, constraints string) {
	root := htmlquery.FindOne(doc, `//span[@class="lang-ja"]`)
	if root == nil {
		root = htmlquery.FindOne(doc, `//span[@class="lang-en"]`)
	}
	if root == nil {
		root = doc
	}
	for _, h := range htmlquery.Find(root, `.//h3`) {
		text := strings.TrimSpace(htmlquery.InnerText(h))
		switch {
		case inputFormat == "" && inputHeadingRe.MatchString(text):
			inputFormat = sectionInput(h)
		case constraints == "" && constraintHeadingRe.MatchString(text):
			constraints = sectionText(h)
		}
	}
	return inputFormat, constraints
}

// sectionInput は入力形式節から書式テンプレートの <pre> を取り出す。
// 節は <div class="part"><section><h3>入力</h3> ... <pre>N M ...</pre></section>。
func sectionInput(h *html.Node) string {
	pre := htmlquery.FindOne(h, `following-sibling::pre[1]`)
	if pre == nil && h.Parent != nil {
		pre = htmlquery.FindOne(h.Parent, `.//pre[1]`)
	}
	if pre == nil {
		return ""
	}
	return normalizeSection(htmlquery.InnerText(pre))
}

// sectionText は節本文 (見出し h3 を除く親 section のテキスト) を取り出す。
func sectionText(h *html.Node) string {
	container := h.Parent
	if container == nil {
		return ""
	}
	full := htmlquery.InnerText(container)
	head := htmlquery.InnerText(h)
	// 先頭に来る見出し文字列を 1 回だけ剥がす。
	full = strings.TrimSpace(full)
	head = strings.TrimSpace(head)
	if strings.HasPrefix(full, head) {
		full = full[len(head):]
	}
	return normalizeSection(full)
}

func normalizeSection(s string) string {
	s = strings.ReplaceAll(s, "\r\n", "\n")
	return strings.Trim(s, "\n ")
}

var timeLimitRe = regexp.MustCompile(`(?:実行時間制限|Time\s*Limit)\s*[:：]?\s*([\d.]+)\s*sec`)

func extractTimeLimit(doc *html.Node) (int, error) {
	text := htmlquery.InnerText(doc)
	m := timeLimitRe.FindStringSubmatch(text)
	if m == nil {
		return 0, fmt.Errorf("time limit not found in page")
	}
	v, err := strconv.ParseFloat(m[1], 64)
	if err != nil {
		return 0, err
	}
	return int(v * 1000), nil
}

var sampleHeadingRe = regexp.MustCompile(`^(入力例|出力例|Sample\s*Input|Sample\s*Output)\s*(\d+)`)

func extractSamples(doc *html.Node) ([]sample, error) {
	root := htmlquery.FindOne(doc, `//span[@class="lang-ja"]`)
	if root == nil {
		root = htmlquery.FindOne(doc, `//span[@class="lang-en"]`)
	}
	if root == nil {
		root = doc
	}

	inputs := make(map[int]string)
	outputs := make(map[int]string)

	headings := htmlquery.Find(root, `.//h3`)
	for _, h := range headings {
		text := strings.TrimSpace(htmlquery.InnerText(h))
		m := sampleHeadingRe.FindStringSubmatch(text)
		if m == nil {
			continue
		}
		n, err := strconv.Atoi(m[2])
		if err != nil {
			continue
		}

		pre := htmlquery.FindOne(h, `following-sibling::pre[1]`)
		if pre == nil {
			pre = htmlquery.FindOne(h.Parent, `.//pre[1]`)
		}
		if pre == nil {
			continue
		}
		body := htmlquery.InnerText(pre)
		body = strings.ReplaceAll(body, "\r\n", "\n")
		// 先頭の改行 (HTML 整形上の余白) だけ落とし、末尾の改行は保持する。
		// abc185_d 入力例 4 の `1 0\n\n` のように、末尾の空行が有意な
		// 入力行 (空の配列) を表すことがあるため Trim で潰してはいけない。
		body = strings.TrimLeft(body, "\n")
		if !strings.HasSuffix(body, "\n") {
			body += "\n"
		}

		isInput := strings.Contains(m[1], "入力") || strings.Contains(m[1], "Input")
		if isInput {
			inputs[n] = body
		} else {
			outputs[n] = body
		}
	}

	maxN := 0
	for k := range inputs {
		if k > maxN {
			maxN = k
		}
	}
	for k := range outputs {
		if k > maxN {
			maxN = k
		}
	}

	var samples []sample
	for i := 1; i <= maxN; i++ {
		in, okIn := inputs[i]
		out, okOut := outputs[i]
		if !okIn && !okOut {
			continue
		}
		if !okIn || !okOut {
			return nil, fmt.Errorf("sample %d: input or output missing", i)
		}
		samples = append(samples, sample{Input: in, Output: out})
	}

	if len(samples) == 0 {
		return nil, fmt.Errorf("no samples found")
	}
	return samples, nil
}
