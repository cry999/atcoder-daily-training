package ui

import (
	"strings"
	"testing"

	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
)

// scrollbar 検証用に overflow した model を作る (height を絞って maxViewportHeight を
// 小さくし、scrollback をスクロール可能にする)。
func scrollbarModel() *chatModel {
	m := &chatModel{width: 40, height: 8, ready: true, mode: modeCommand}
	m.viewport = viewport.New(m.contentWidth(), 3)
	for i := 0; i < 30; i++ {
		m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "line"})
	}
	m.refreshViewport()
	return m
}

// 各行が gutter 1 列 (track/thumb/空白いずれか) で終わっていることを確認するヘルパ。
func lastRunes(s string) []rune {
	lines := strings.Split(s, "\n")
	out := make([]rune, len(lines))
	for i, ln := range lines {
		r := []rune(ln)
		if len(r) == 0 {
			out[i] = ' '
			continue
		}
		out[i] = r[len(r)-1]
	}
	return out
}

// 要件 056: scrollback がスクロール可能なら右端に track+thumb のスクロールバーが出る。
func TestScrollbar_VisibleWhenScrollable(t *testing.T) {
	m := scrollbarModel()
	if m.viewport.TotalLineCount() <= m.viewport.Height {
		t.Fatalf("test setup: expected overflow (total=%d height=%d)", m.viewport.TotalLineCount(), m.viewport.Height)
	}
	view := m.renderViewport()
	last := lastRunes(view)
	thumbs, tracks := 0, 0
	for _, r := range last {
		switch r {
		case '█':
			thumbs++
		case '│':
			tracks++
		case ' ':
			// 許容しない (scrollable なら全行 track/thumb のはず)
		}
	}
	if thumbs == 0 {
		t.Fatalf("scrollable viewport should render a thumb (█); got gutter %q", string(last))
	}
	if tracks == 0 {
		t.Fatalf("scrollable viewport should render track (│) around the thumb; got gutter %q", string(last))
	}
	if thumbs+tracks != len(last) {
		t.Fatalf("every viewport row should carry a scrollbar cell; gutter=%q", string(last))
	}
}

// 最下部 (追従中) では thumb は gutter の下端にある。
func TestScrollbar_ThumbAtBottomWhenFollowing(t *testing.T) {
	m := scrollbarModel()
	if !m.viewport.AtBottom() {
		t.Fatal("freshly refreshed viewport should be at the bottom")
	}
	last := lastRunes(m.renderViewport())
	if last[len(last)-1] != '█' {
		t.Fatalf("thumb should sit at the bottom row when following; gutter=%q", string(last))
	}
}

// 上スクロールすると thumb が上へ動く (上端が下端より上になる)。
func TestScrollbar_ThumbMovesUpOnScroll(t *testing.T) {
	m := scrollbarModel()
	bottom := lastRunes(m.renderViewport())

	// PageUp で最上部近くまで遡る。
	for i := 0; i < 20 && !m.viewport.AtTop(); i++ {
		m.updateCommand(tea.KeyMsg{Type: tea.KeyPgUp})
	}
	top := lastRunes(m.renderViewport())

	firstThumb := func(rs []rune) int {
		for i, r := range rs {
			if r == '█' {
				return i
			}
		}
		return -1
	}
	tb, tt := firstThumb(bottom), firstThumb(top)
	if tb < 0 || tt < 0 {
		t.Fatalf("expected a thumb in both states (bottom=%q top=%q)", string(bottom), string(top))
	}
	if tt >= tb {
		t.Fatalf("thumb should move up after scrolling up: top-first=%d bottom-first=%d", tt, tb)
	}
	if !m.viewport.AtTop() {
		t.Fatal("setup: expected to reach the top")
	}
	if top[0] != '█' {
		t.Fatalf("at the top the thumb should include the first row; gutter=%q", string(top))
	}
}

// scrollback が 1 画面に収まるときは gutter が空白 (スクロールバー非表示)。
func TestScrollbar_BlankWhenFits(t *testing.T) {
	m := &chatModel{width: 40, height: 20, ready: true, mode: modeInsert}
	m.viewport = viewport.New(m.contentWidth(), 1)
	m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "only line"})
	m.refreshViewport()
	if m.viewport.TotalLineCount() > m.viewport.Height {
		t.Fatalf("test setup: expected content to fit (total=%d height=%d)", m.viewport.TotalLineCount(), m.viewport.Height)
	}
	for _, r := range lastRunes(m.renderViewport()) {
		if r == '█' || r == '│' {
			t.Fatalf("non-scrollable viewport must not draw a scrollbar; got %q", r)
		}
	}
}

// 端末幅が狭い (width<2) ときはスクロールバー列を足さない (本文が全幅を使う)。
func TestScrollbar_SkippedWhenTooNarrow(t *testing.T) {
	m := scrollbarModel()
	m.width = 1
	m.viewport.Width = m.contentWidth()
	m.refreshViewport()
	got := m.renderViewport()
	if got != m.viewport.View() {
		t.Fatal("width<2 should return the bare viewport with no scrollbar column appended")
	}
}

// gutter を 1 列確保するので本文の折り返し幅は width-1 になる (リフロー回避の前提)。
func TestScrollbar_ContentWidthReservesGutter(t *testing.T) {
	m := &chatModel{width: 40, height: 8, ready: true}
	if got := m.contentWidth(); got != 39 {
		t.Fatalf("contentWidth should reserve 1 gutter column: want 39 got %d", got)
	}
	m.width = 1
	if got := m.contentWidth(); got != 1 {
		t.Fatalf("width=1 has no room to reserve: want 1 got %d", got)
	}
}
