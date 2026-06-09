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
}

func fetchProblem(contest, task string) (*problem, error) {
	url := fmt.Sprintf("https://atcoder.jp/contests/%s/tasks/%s", contest, task)
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

	return &problem{
		URL:         url,
		TimeLimitMs: tlMs,
		Samples:     samples,
	}, nil
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
		body = strings.Trim(body, "\n")
		body += "\n"

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
