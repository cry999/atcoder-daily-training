package ui

import (
	"errors"
	"strings"
	"testing"
)

// :meta は parseCommand で name="meta" になり、フィールド/値は arg に載る (要件 055)。
func TestParseCommandMeta(t *testing.T) {
	cases := []struct {
		in      string
		wantArg string
	}{
		{"meta", ""},
		{"meta url", "url"},
		{"meta url https://atcoder.jp/contests/abc111/tasks/arc103_b", "url https://atcoder.jp/contests/abc111/tasks/arc103_b"},
		{"meta time_limit 5s", "time_limit 5s"},
	}
	for _, c := range cases {
		got := parseCommand(c.in)
		if got.name != "meta" || got.arg != c.wantArg {
			t.Errorf("parseCommand(%q) = {name:%q arg:%q}, want {name:%q arg:%q}", c.in, got.name, got.arg, "meta", c.wantArg)
		}
	}
}

// fake フックを仕込んだ chatModel を作る。show/set/fetch の呼び出しを記録する。
type metaSpy struct {
	showField  string
	setField   string
	setValue   string
	showLines  []string
	setLines   []string
	setTLMs    int
	showErr    error
	setErr     error
	fetchCalls int
	fetchLines []string
	fetchTLMs  int
	fetchErr   error
}

func modelWithMeta(spy *metaSpy) *chatModel {
	return &chatModel{header: ChatHeader{
		MetaShow: func(field string) ([]string, error) {
			spy.showField = field
			return spy.showLines, spy.showErr
		},
		MetaSet: func(field, value string) ([]string, int, error) {
			spy.setField, spy.setValue = field, value
			return spy.setLines, spy.setTLMs, spy.setErr
		},
		MetaFetch: func() ([]string, int, error) {
			spy.fetchCalls++
			return spy.fetchLines, spy.fetchTLMs, spy.fetchErr
		},
	}}
}

func lastN(m *chatModel, n int) []chatLine {
	return m.msgs[len(m.msgs)-n:]
}

// :meta (引数なし) は MetaShow を field="" で呼び、返った行を info 行で積む。
func TestExecMetaShowAll(t *testing.T) {
	spy := &metaSpy{showLines: []string{"url:         https://x", "time limit:  2000 ms", "samples:     3"}}
	m := modelWithMeta(spy)

	m.execMeta("")

	if spy.showField != "" {
		t.Fatalf("MetaShow field=%q, want empty", spy.showField)
	}
	got := lastN(m, 3)
	for i, want := range spy.showLines {
		if got[i].kind != kindInfo || got[i].text != want {
			t.Fatalf("line %d = {%q %q}, want {info %q}", i, got[i].kind, got[i].text, want)
		}
	}
}

// :meta url (値なし) は MetaShow を field="url" で呼ぶ。
func TestExecMetaShowField(t *testing.T) {
	spy := &metaSpy{showLines: []string{"url:         https://x"}}
	m := modelWithMeta(spy)

	m.execMeta("url")

	if spy.showField != "url" {
		t.Fatalf("MetaShow field=%q, want url", spy.showField)
	}
	if last := m.msgs[len(m.msgs)-1]; last.text != "url:         https://x" {
		t.Fatalf("text=%q", last.text)
	}
}

// :meta url <url> は MetaSet を field="url" で呼び、結果行を積む。time_limit ではないので
// ヘッダの TimeLimitMs は変えない。
func TestExecMetaSetURL(t *testing.T) {
	spy := &metaSpy{setLines: []string{"url:         (none) -> https://y"}, setTLMs: 2000}
	m := modelWithMeta(spy)
	m.header.TimeLimitMs = 1000

	m.execMeta("url https://atcoder.jp/contests/abc111/tasks/arc103_b")

	if spy.setField != "url" || spy.setValue != "https://atcoder.jp/contests/abc111/tasks/arc103_b" {
		t.Fatalf("MetaSet(%q, %q)", spy.setField, spy.setValue)
	}
	if m.header.TimeLimitMs != 1000 {
		t.Fatalf("TimeLimitMs changed to %d on url edit, want 1000", m.header.TimeLimitMs)
	}
	if last := m.msgs[len(m.msgs)-1]; last.kind != kindInfo || !strings.Contains(last.text, "-> https://y") {
		t.Fatalf("line = {%q %q}", last.kind, last.text)
	}
}

// :meta time_limit <dur> は MetaSet を field="time_limit" で呼び、成功時にヘッダの
// TimeLimitMs を新値へ更新する (続く :test の TLE 判定に効く)。
func TestExecMetaSetTimeLimit(t *testing.T) {
	spy := &metaSpy{setLines: []string{"time limit:  2000 ms -> 5000 ms"}, setTLMs: 5000}
	m := modelWithMeta(spy)
	m.header.TimeLimitMs = 2000

	m.execMeta("time_limit 5s")

	if spy.setField != "time_limit" || spy.setValue != "5s" {
		t.Fatalf("MetaSet(%q, %q)", spy.setField, spy.setValue)
	}
	if m.header.TimeLimitMs != 5000 {
		t.Fatalf("TimeLimitMs=%d, want 5000 (header should follow time_limit edit)", m.header.TimeLimitMs)
	}
}

// 未知フィールドは E518 を出し、フックは呼ばない。
func TestExecMetaUnknownField(t *testing.T) {
	spy := &metaSpy{}
	m := modelWithMeta(spy)

	m.execMeta("foo bar")

	if spy.setField != "" || spy.showField != "" {
		t.Fatalf("hooks should not be called for unknown field")
	}
	if last := m.msgs[len(m.msgs)-1]; !strings.HasPrefix(last.text, "E518:") {
		t.Fatalf("text=%q, want E518 prefix", last.text)
	}
}

// set が error を返したら err 行で表示し、chat は継続する (ヘッダは変えない)。
func TestExecMetaSetError(t *testing.T) {
	spy := &metaSpy{setErr: errors.New("--time-limit は正の値で指定してください (例: 5s, 1500ms)")}
	m := modelWithMeta(spy)
	m.header.TimeLimitMs = 2000

	m.execMeta("time_limit 0")

	last := m.msgs[len(m.msgs)-1]
	if last.kind != kindErr || !strings.Contains(last.text, "正の値") {
		t.Fatalf("line = {%q %q}, want err with reason", last.kind, last.text)
	}
	if m.header.TimeLimitMs != 2000 {
		t.Fatalf("TimeLimitMs changed to %d on set error, want 2000", m.header.TimeLimitMs)
	}
}

// show が error を返したら err 行で表示する (未キャッシュ等)。
func TestExecMetaShowError(t *testing.T) {
	spy := &metaSpy{showErr: errors.New("meta が未取得です")}
	m := modelWithMeta(spy)

	m.execMeta("")

	if last := m.msgs[len(m.msgs)-1]; last.kind != kindErr || !strings.Contains(last.text, "未取得") {
		t.Fatalf("line = {%q %q}", last.kind, last.text)
	}
}

// MetaShow/MetaSet 未注入 (nil) のとき :meta は「使えません」を 1 行出すだけ (パニックしない)。
func TestExecMetaUnavailable(t *testing.T) {
	m := &chatModel{header: ChatHeader{}} // フック nil

	m.execMeta("url https://x")

	if last := m.msgs[len(m.msgs)-1]; !strings.Contains(last.text, "使えません") {
		t.Fatalf("text=%q", last.text)
	}
}

// :meta fetch は parseCommand で name="meta" / arg="fetch" になる (要件 057)。
func TestParseCommandMetaFetch(t *testing.T) {
	got := parseCommand("meta fetch")
	if got.name != "meta" || got.arg != "fetch" {
		t.Fatalf("parseCommand(meta fetch) = {name:%q arg:%q}, want {meta fetch}", got.name, got.arg)
	}
}

// :meta fetch は「(再取得中…)」を即積み、非同期の tea.Cmd を返す。その cmd は MetaFetch を
// 呼んで metaFetchDoneMsg を返す (要件 057)。
func TestExecMetaFetch(t *testing.T) {
	spy := &metaSpy{fetchLines: []string{"fetched abc111_d", "time limit:  2000 ms", "samples:     3"}, fetchTLMs: 2000}
	m := modelWithMeta(spy)

	cmd := m.execMeta("fetch")

	if last := m.msgs[len(m.msgs)-1]; !strings.Contains(last.text, "再取得中") {
		t.Fatalf("先頭に進捗行が無い: text=%q", last.text)
	}
	if cmd == nil {
		t.Fatal("execMeta(fetch) は非同期 cmd を返すべき (nil だった)")
	}
	msg := cmd()
	done, ok := msg.(metaFetchDoneMsg)
	if !ok {
		t.Fatalf("cmd() = %T, want metaFetchDoneMsg", msg)
	}
	if spy.fetchCalls != 1 {
		t.Fatalf("MetaFetch 呼び出し回数 = %d, want 1", spy.fetchCalls)
	}
	if done.newTimeLimitMs != 2000 || len(done.lines) != 3 {
		t.Fatalf("metaFetchDoneMsg = %+v", done)
	}
}

// applyMetaFetchDone 成功: 結果行を info で積み、Time Limit が変わっていればヘッダを更新する。
func TestApplyMetaFetchDoneSuccess(t *testing.T) {
	m := &chatModel{header: ChatHeader{}}
	m.header.TimeLimitMs = 2000

	m.applyMetaFetchDone(metaFetchDoneMsg{
		lines:          []string{"fetched abc111_d", "time limit:  5000 ms", "samples:     2"},
		newTimeLimitMs: 5000,
	})

	if m.header.TimeLimitMs != 5000 {
		t.Fatalf("TimeLimitMs=%d, want 5000 (再取得で TL が変わったらヘッダも追従)", m.header.TimeLimitMs)
	}
	got := lastN(m, 3)
	for i, want := range []string{"fetched abc111_d", "time limit:  5000 ms", "samples:     2"} {
		if got[i].kind != kindInfo || got[i].text != want {
			t.Fatalf("line %d = {%q %q}, want {info %q}", i, got[i].kind, got[i].text, want)
		}
	}
}

// applyMetaFetchDone 失敗: err 行を 1 本積み、ヘッダは変えない。
func TestApplyMetaFetchDoneError(t *testing.T) {
	m := &chatModel{header: ChatHeader{}}
	m.header.TimeLimitMs = 2000

	m.applyMetaFetchDone(metaFetchDoneMsg{err: errors.New("再取得に失敗しました: network")})

	last := m.msgs[len(m.msgs)-1]
	if last.kind != kindErr || !strings.Contains(last.text, "失敗") {
		t.Fatalf("line = {%q %q}, want err with reason", last.kind, last.text)
	}
	if m.header.TimeLimitMs != 2000 {
		t.Fatalf("TimeLimitMs changed to %d on fetch error, want 2000", m.header.TimeLimitMs)
	}
}

// MetaFetch 未注入 (nil) のとき :meta fetch は「使えません」を 1 行出し、cmd は返さない。
func TestExecMetaFetchUnavailable(t *testing.T) {
	// MetaShow/MetaSet はあるが MetaFetch だけ nil のケース (防御的ガード)。
	m := &chatModel{header: ChatHeader{
		MetaShow: func(string) ([]string, error) { return nil, nil },
		MetaSet:  func(string, string) ([]string, int, error) { return nil, 0, nil },
	}}

	cmd := m.execMeta("fetch")

	if cmd != nil {
		t.Fatal("MetaFetch nil のとき cmd は nil であるべき")
	}
	if last := m.msgs[len(m.msgs)-1]; !strings.Contains(last.text, "使えません") {
		t.Fatalf("text=%q", last.text)
	}
}
