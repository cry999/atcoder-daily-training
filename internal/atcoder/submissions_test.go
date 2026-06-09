package atcoder

import (
	"strings"
	"testing"

	"github.com/antchfx/htmlquery"
	"golang.org/x/net/html"
)

// NOTE: /submissions/me はログイン必須で、この環境からは実物の HTML を取得
// できない。以下のフィクスチャは AtCoder の既知のテーブル構造 (列順: 提出日時 |
// 問題 | ユーザ | 言語 | 得点 | コード長 | 結果 | 実行時間 | メモリ | 詳細) を
// 忠実に再現したものだが、実環境の HTML 形状はユーザのアカウントでの検証が
// 別途必要。レイアウト変更時はここを実物に合わせて更新すること。

// fixtureDoc は HTML 文字列を golang.org/x/net/html でパースして
// parseSubmissions に渡せる *html.Node を返す。
func fixtureDoc(t *testing.T, htmlStr string) *html.Node {
	t.Helper()
	doc, err := htmlquery.Parse(strings.NewReader(htmlStr))
	if err != nil {
		t.Fatalf("fixture HTML のパースに失敗: %v", err)
	}
	return doc
}

// 確定 AC 行。実行時間・メモリ・言語リンクをすべて備える典型形。
const rowAC = `
<tr>
  <td class="no-break"><time class="fixtime fixtime-second">2022-07-09 21:34:56+0900</time></td>
  <td><a href="/contests/abc258/tasks/abc258_d">D - Trophy</a></td>
  <td><a href="/users/takeharak999">takeharak999</a></td>
  <td><a href="/contests/abc258/submissions?f.Language=4047">Python (PyPy 3.11-v7.3.20)</a></td>
  <td class="text-right">400</td>
  <td class="text-right">1234 Byte</td>
  <td class="text-center"><span class="label label-success">AC</span></td>
  <td class="text-right">91 ms</td>
  <td class="text-right">108556 KB</td>
  <td class="text-center"><a href="/contests/abc258/submissions/76544704">Detail</a></td>
</tr>`

// 確定 WA 行。別 ID・別 task。
const rowWA = `
<tr>
  <td class="no-break"><time class="fixtime fixtime-second">2022-07-09 21:30:00+0900</time></td>
  <td><a href="/contests/abc258/tasks/abc258_c">C - Rotation</a></td>
  <td><a href="/users/takeharak999">takeharak999</a></td>
  <td><a href="/contests/abc258/submissions?f.Language=5078">C++ 23 (gcc 12.2)</a></td>
  <td class="text-right">0</td>
  <td class="text-right">567 Byte</td>
  <td class="text-center"><span class="label label-warning">WA</span></td>
  <td class="text-right">12 ms</td>
  <td class="text-right">3456 KB</td>
  <td class="text-center"><a href="/contests/abc258/submissions/76544000">Detail</a></td>
</tr>`

// ジャッジ中行。結果ラベルが WJ で、実行時間・メモリ列が欠落している。
const rowWJ = `
<tr>
  <td class="no-break"><time class="fixtime fixtime-second">2022-07-09 21:40:00+0900</time></td>
  <td><a href="/contests/abc258/tasks/abc258_e">E - Packing Potatoes</a></td>
  <td><a href="/users/takeharak999">takeharak999</a></td>
  <td><a href="/contests/abc258/submissions?f.Language=4047">Python (PyPy 3.11-v7.3.20)</a></td>
  <td class="text-right">0</td>
  <td class="text-right">890 Byte</td>
  <td class="text-center"><span class="label label-warning">WJ</span></td>
  <td class="text-center"><a href="/contests/abc258/submissions/76545000">Detail</a></td>
</tr>`

// 提出 ID リンクの無いヘッダ風の行。スキップされるべき。
const rowNoSubmission = `
<tr>
  <td><a href="/contests/abc258/tasks/abc258_a">A - When?</a></td>
  <td>not a real submission row</td>
</tr>`

func wrapTable(rows ...string) string {
	var b strings.Builder
	b.WriteString(`<html><body><table class="table table-bordered table-striped small th-center">`)
	b.WriteString(`<thead><tr><th>提出日時</th><th>問題</th><th>ユーザ</th><th>言語</th><th>得点</th><th>コード長</th><th>結果</th><th>実行時間</th><th>メモリ</th><th></th></tr></thead>`)
	b.WriteString(`<tbody>`)
	for _, r := range rows {
		b.WriteString(r)
	}
	b.WriteString(`</tbody></table></body></html>`)
	return b.String()
}

func findSub(subs []Submission, id int) (Submission, bool) {
	for _, s := range subs {
		if s.ID == id {
			return s, true
		}
	}
	return Submission{}, false
}

func TestParseSubmissions_AC(t *testing.T) {
	doc := fixtureDoc(t, wrapTable(rowAC))
	subs := parseSubmissions(doc, "abc258")
	if len(subs) != 1 {
		t.Fatalf("提出件数 = %d, want 1", len(subs))
	}
	s := subs[0]
	if s.ID != 76544704 {
		t.Errorf("ID = %d, want 76544704", s.ID)
	}
	if s.Task != "abc258_d" {
		t.Errorf("Task = %q, want abc258_d", s.Task)
	}
	if s.TaskTitle != "D - Trophy" {
		t.Errorf("TaskTitle = %q, want %q", s.TaskTitle, "D - Trophy")
	}
	if s.Verdict != "AC" {
		t.Errorf("Verdict = %q, want AC", s.Verdict)
	}
	if s.ExecTimeMs != 91 {
		t.Errorf("ExecTimeMs = %d, want 91", s.ExecTimeMs)
	}
	if s.MemoryKiB != 108556 {
		t.Errorf("MemoryKiB = %d, want 108556", s.MemoryKiB)
	}
	if !strings.HasSuffix(s.URL, "/submissions/76544704") {
		t.Errorf("URL = %q, want suffix /submissions/76544704", s.URL)
	}
	if s.Language != "Python (PyPy 3.11-v7.3.20)" {
		t.Errorf("Language = %q, want %q", s.Language, "Python (PyPy 3.11-v7.3.20)")
	}
	if !IsFinal(s.Verdict) {
		t.Errorf("IsFinal(%q) = false, want true", s.Verdict)
	}
	if s.SubmittedAt.IsZero() {
		t.Errorf("SubmittedAt がゼロ値: パースできていない")
	}
}

func TestParseSubmissions_WA(t *testing.T) {
	doc := fixtureDoc(t, wrapTable(rowWA))
	subs := parseSubmissions(doc, "abc258")
	if len(subs) != 1 {
		t.Fatalf("提出件数 = %d, want 1", len(subs))
	}
	s := subs[0]
	if s.ID != 76544000 {
		t.Errorf("ID = %d, want 76544000", s.ID)
	}
	if s.Task != "abc258_c" {
		t.Errorf("Task = %q, want abc258_c", s.Task)
	}
	if s.Verdict != "WA" {
		t.Errorf("Verdict = %q, want WA", s.Verdict)
	}
	if s.Language != "C++ 23 (gcc 12.2)" {
		t.Errorf("Language = %q, want %q", s.Language, "C++ 23 (gcc 12.2)")
	}
	if !IsFinal(s.Verdict) {
		t.Errorf("IsFinal(WA) = false, want true")
	}
}

func TestParseSubmissions_Judging(t *testing.T) {
	doc := fixtureDoc(t, wrapTable(rowWJ))
	subs := parseSubmissions(doc, "abc258")
	if len(subs) != 1 {
		t.Fatalf("提出件数 = %d, want 1", len(subs))
	}
	s := subs[0]
	if s.ID != 76545000 {
		t.Errorf("ID = %d, want 76545000", s.ID)
	}
	if s.Task != "abc258_e" {
		t.Errorf("Task = %q, want abc258_e", s.Task)
	}
	if s.Verdict != "WJ" {
		t.Errorf("Verdict = %q, want WJ", s.Verdict)
	}
	// 実行時間・メモリ列が欠落していても 0 のまま・panic しない。
	if s.ExecTimeMs != 0 {
		t.Errorf("ExecTimeMs = %d, want 0 (ジャッジ中)", s.ExecTimeMs)
	}
	if s.MemoryKiB != 0 {
		t.Errorf("MemoryKiB = %d, want 0 (ジャッジ中)", s.MemoryKiB)
	}
	if IsFinal(s.Verdict) {
		t.Errorf("IsFinal(WJ) = true, want false")
	}
}

func TestParseSubmissions_MultipleNewestFirst(t *testing.T) {
	// AtCoder は新しい順で返す。行の並び順がそのまま保たれることを確認。
	doc := fixtureDoc(t, wrapTable(rowWJ, rowAC, rowWA))
	subs := parseSubmissions(doc, "abc258")
	if len(subs) != 3 {
		t.Fatalf("提出件数 = %d, want 3", len(subs))
	}
	wantOrder := []int{76545000, 76544704, 76544000}
	for i, want := range wantOrder {
		if subs[i].ID != want {
			t.Errorf("subs[%d].ID = %d, want %d", i, subs[i].ID, want)
		}
	}
}

func TestParseSubmissions_SkipsNonSubmissionRows(t *testing.T) {
	// 提出 ID リンクの無い行は ID 0 として除外される。
	doc := fixtureDoc(t, wrapTable(rowNoSubmission, rowAC))
	subs := parseSubmissions(doc, "abc258")
	if len(subs) != 1 {
		t.Fatalf("提出件数 = %d, want 1 (非提出行はスキップ)", len(subs))
	}
	if subs[0].ID != 76544704 {
		t.Errorf("残った提出 ID = %d, want 76544704", subs[0].ID)
	}
	if _, ok := findSub(subs, 0); ok {
		t.Errorf("ID 0 の行が混入している")
	}
}

func TestParseSubmissions_NilDoc(t *testing.T) {
	// nil ノードでも panic しない。
	if got := parseSubmissions(nil, "abc258"); got != nil {
		t.Errorf("parseSubmissions(nil) = %v, want nil", got)
	}
}

func TestParseRow_NilRow(t *testing.T) {
	// 短い行・nil 行でも panic しない。
	s := parseRow(nil, "abc258")
	if s.ID != 0 {
		t.Errorf("parseRow(nil).ID = %d, want 0", s.ID)
	}
}

func TestIsFinal(t *testing.T) {
	cases := []struct {
		verdict string
		want    bool
	}{
		{"AC", true},
		{"WA", true},
		{"TLE", true},
		{"RE", true},
		{"CE", true},
		{"MLE", true},
		{"WJ", false},
		{"WR", false},
		{"", false},
		{"   ", false},
		{"Judging 3/21", false},
		{"Judging", false},
	}
	for _, c := range cases {
		if got := IsFinal(c.verdict); got != c.want {
			t.Errorf("IsFinal(%q) = %v, want %v", c.verdict, got, c.want)
		}
	}
}
