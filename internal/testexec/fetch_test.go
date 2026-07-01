package testexec

import (
	"strings"
	"testing"

	"golang.org/x/net/html"
)

// resolveFetchURL は url override があればそれを優先し、無ければ contest/task から
// 導出する。task_id が contest と食い違う問題 (abc111 D = arc103_b) で、override が
// 効くことを固定する。
func TestResolveFetchURL(t *testing.T) {
	cases := []struct {
		contest, task, override, want string
	}{
		{"abc457", "abc457_d", "", "https://atcoder.jp/contests/abc457/tasks/abc457_d"},
		// override 優先: スロットは abc111/abc111_d のまま arc103_b のページを引く。
		{"abc111", "abc111_d", "https://atcoder.jp/contests/abc111/tasks/arc103_b", "https://atcoder.jp/contests/abc111/tasks/arc103_b"},
	}
	for _, c := range cases {
		if got := resolveFetchURL(c.contest, c.task, c.override); got != c.want {
			t.Errorf("resolveFetchURL(%q, %q, %q) = %q, want %q", c.contest, c.task, c.override, got, c.want)
		}
	}
}

// letterIndex は <contest>_<letter> の末尾 letter を 0 始まりの序数に直す。
// 一覧ページ解決 (要件 065) で letter → 出現順 index の対応に使うため、
// 単一英小文字だけを受け付け、それ以外は解決を諦める (ok=false) ことを固定する。
func TestLetterIndex(t *testing.T) {
	cases := []struct {
		task    string
		wantIdx int
		wantOK  bool
	}{
		{"abc111_a", 0, true},
		{"abc111_d", 3, true},
		{"abc457_h", 7, true},
		{"arc103_b", 1, true},
		{"abc111_ex", 0, false}, // 複数文字の letter は非対応
		{"abc111_A", 0, false},  // 大文字は非対応
		{"abc111_1", 0, false},  // 数字は非対応
		{"abc111", 0, false},    // アンダースコア無し
	}
	for _, c := range cases {
		idx, ok := letterIndex(c.task)
		if ok != c.wantOK || (ok && idx != c.wantIdx) {
			t.Errorf("letterIndex(%q) = (%d, %v), want (%d, %v)", c.task, idx, ok, c.wantIdx, c.wantOK)
		}
	}
}

// extractSamples が末尾の空行 (有意な空入力行) を保持することを確認する。
// abc185_d の入力例 4 (`1 0` の後に空の A 行) のように、空行を落とすと
// 解答側の input() が EOF エラーになるため、pre の内容をそのまま残す必要がある。
func TestExtractSamplesPreservesTrailingBlankLine(t *testing.T) {
	const page = `<html><body><span class="lang-ja">
<div class="part"><h3>入力例 1</h3><pre>5 2
1 3
</pre></div>
<div class="part"><h3>出力例 1</h3><pre>3
</pre></div>
<div class="part"><h3>入力例 2</h3><pre>1 0

</pre></div>
<div class="part"><h3>出力例 2</h3><pre>1
</pre></div>
</span></body></html>`

	doc, err := html.Parse(strings.NewReader(page))
	if err != nil {
		t.Fatalf("html.Parse: %v", err)
	}

	samples, err := extractSamples(doc)
	if err != nil {
		t.Fatalf("extractSamples: %v", err)
	}
	if len(samples) != 2 {
		t.Fatalf("len(samples) = %d, want 2", len(samples))
	}

	if got, want := samples[0].Input, "5 2\n1 3\n"; got != want {
		t.Errorf("sample 1 Input = %q, want %q", got, want)
	}
	// 末尾の空行が保持されていること (`1 0\n\n`)。
	if got, want := samples[1].Input, "1 0\n\n"; got != want {
		t.Errorf("sample 2 Input = %q, want %q", got, want)
	}
}
