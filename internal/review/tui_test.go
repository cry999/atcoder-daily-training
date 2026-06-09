package review

import (
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// sampleReport は TUI テスト用の小さな Report を作る。
func sampleReport(t *testing.T) Report {
	t.Helper()
	now := d(2026, 6, 9)
	solves := []stats.Solve{
		sv(d(2026, 6, 8), "abc458", "d"),
		sv(d(2026, 6, 7), "abc457", "d"),
	}
	return Build(solves, Options{Category: "abc", Now: now})
}

func TestReviewModelSizingAndView(t *testing.T) {
	m := newReviewModel(sampleReport(t))

	// WindowSizeMsg 前は未準備。
	if m.ready {
		t.Fatal("model should not be ready before WindowSizeMsg")
	}

	// サイズ確定で viewport が立ち上がる。
	updated, _ := m.Update(tea.WindowSizeMsg{Width: 80, Height: 24})
	rm := updated.(reviewModel)
	if !rm.ready {
		t.Fatal("model should be ready after WindowSizeMsg")
	}
	if rm.vp.Height != 24-chromeHeight {
		t.Errorf("viewport height = %d, want %d", rm.vp.Height, 24-chromeHeight)
	}

	// View が固定ヘッダ・列ヘッダ・凡例・件数・ヘルプを含む (panic しない)。
	view := rm.View()
	for _, want := range []string{"abc review", "contest", "last solved", "older", "2 contests", "q quit"} {
		if !strings.Contains(view, want) {
			t.Errorf("View missing %q\n---\n%s", want, view)
		}
	}
}

func TestReviewModelQuitKey(t *testing.T) {
	m := newReviewModel(sampleReport(t))
	updated, _ := m.Update(tea.WindowSizeMsg{Width: 80, Height: 24})

	for _, msg := range []tea.KeyMsg{
		{Type: tea.KeyRunes, Runes: []rune("q")},
		{Type: tea.KeyEsc},
		{Type: tea.KeyCtrlC},
	} {
		_, cmd := updated.(reviewModel).Update(msg)
		if cmd == nil {
			t.Errorf("key %q: expected a quit command, got nil", msg.String())
			continue
		}
		if _, ok := cmd().(tea.QuitMsg); !ok {
			t.Errorf("key %q: command did not produce tea.QuitMsg", msg.String())
		}
	}
}
