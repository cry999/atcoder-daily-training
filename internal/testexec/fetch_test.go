package testexec

import (
	"strings"
	"testing"

	"golang.org/x/net/html"
)

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
