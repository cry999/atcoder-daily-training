package testexec

import (
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/antchfx/htmlquery"
	"golang.org/x/net/html"
)

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
	return fmt.Sprintf("https://atcoder.jp/contests/%s/tasks/%s", contest, task)
}

// resolveFetchURL は取得元 URL を決める。override (meta.toml の url) が空でなければ
// それを優先し、空なら contest/task から導出する。
func resolveFetchURL(contest, task, override string) string {
	if override != "" {
		return override
	}
	return DefaultTaskURL(contest, task)
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
		return nil, fmt.Errorf("HTTP %d for %s", resp.StatusCode, url)
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
