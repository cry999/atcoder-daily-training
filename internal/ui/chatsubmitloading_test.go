package ui

import (
	"strings"
	"testing"

	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
)

// SubmitCheck が注入されていると Ctrl+S はチェックを同期実行せず、
// スピナー tick + チェック本体を走らせる tea.Cmd を返して「準備中」を出す。
func TestChatCtrlS_ShowsLoadingWhileChecking(t *testing.T) {
	m := initialChatModel(ChatHeader{
		Submit:      func() SubmitResult { return SubmitResult{Message: "ok"} },
		SubmitCheck: func() SubmitCheck { return SubmitCheck{Clean: true} },
	}, nil)
	m.width, m.height, m.ready = 40, 20, true
	m.viewport = viewport.New(40, 5)

	m, cmd := ctrlS(m)

	if !m.submitChecking {
		t.Fatal("Ctrl+S with SubmitCheck should enter submitChecking state")
	}
	if cmd == nil {
		t.Fatal("Ctrl+S with SubmitCheck should return a cmd (spinner tick + async check)")
	}
	// チェックはまだ走っていない (非同期): 提出結果はこの時点で積まれていない。
	for _, msg := range m.msgs {
		if strings.Contains(msg.text, "提出準備:") {
			t.Fatalf("submit result should not appear before the async check completes: %q", msg.text)
		}
	}
	// 出力末尾に「提出前準備中」スピナーが出る。
	m.refreshViewport()
	if !strings.Contains(m.viewport.View(), "提出前準備中") {
		t.Errorf("viewport tail should show 提出前準備中 while checking: %q", m.viewport.View())
	}
}

// 準備中に届いた submitCheckMsg (clean) はスピナーを止め、提出準備を実行する。
func TestChatSubmitCheckMsg_CleanSubmits(t *testing.T) {
	submitted := 0
	m := initialChatModel(ChatHeader{
		Submit:      func() SubmitResult { submitted++; return SubmitResult{Message: "abc457/d.py"} },
		SubmitCheck: func() SubmitCheck { return SubmitCheck{Clean: true} },
	}, nil)
	m, _ = ctrlS(m)

	m, _ = func() (*chatModel, tea.Cmd) {
		model, cmd := m.Update(submitCheckMsg{check: SubmitCheck{Clean: true}})
		return model.(*chatModel), cmd
	}()

	if m.submitChecking {
		t.Fatal("submitCheckMsg should clear submitChecking")
	}
	if submitted != 1 {
		t.Fatalf("clean check should call Submit once, got %d", submitted)
	}
	last := m.msgs[len(m.msgs)-1]
	if !strings.Contains(last.text, "提出準備:") {
		t.Fatalf("last line should be the submit result: %q", last.text)
	}
}

// 準備中に届いた submitCheckMsg (dirty) はスピナーを止め、理由を出して確認待ちに入る。
func TestChatSubmitCheckMsg_DirtyConfirms(t *testing.T) {
	m := initialChatModel(ChatHeader{
		Submit: func() SubmitResult { return SubmitResult{Message: "ok"} },
		SubmitCheck: func() SubmitCheck {
			return SubmitCheck{Clean: false, Reasons: []string{"サンプルが全通過していません"}}
		},
	}, nil)
	m, _ = ctrlS(m)

	model, _ := m.Update(submitCheckMsg{check: SubmitCheck{Clean: false, Reasons: []string{"サンプルが全通過していません"}}})
	m = model.(*chatModel)

	if m.submitChecking {
		t.Fatal("submitCheckMsg should clear submitChecking")
	}
	if !m.submitConfirm {
		t.Fatal("a dirty check should enter y/N confirm mode")
	}
	joined := ""
	for _, msg := range m.msgs {
		joined += msg.text + "\n"
	}
	if !strings.Contains(joined, "サンプルが全通過していません") {
		t.Errorf("dirty reasons should be shown: %q", joined)
	}
}

// チェック中に restart が入ると submitChecking は下ろされ、後から届く古い epoch の
// submitCheckMsg は破棄される (reload 前のファイル状態で提出準備が走らない)。
func TestChatSubmitCheckMsg_StaleEpochDiscarded(t *testing.T) {
	submitted := 0
	m := initialChatModel(ChatHeader{
		Submit:      func() SubmitResult { submitted++; return SubmitResult{Message: "ok"} },
		SubmitCheck: func() SubmitCheck { return SubmitCheck{Clean: true} },
	}, nil)
	m, _ = ctrlS(m) // epoch = sessionN = 0 でチェック開始
	if !m.submitChecking {
		t.Fatal("precondition: should be checking")
	}
	// restart 相当: セッションが進み submitChecking が下りる。
	m.sessionN++
	m.submitChecking = false
	// 古い epoch=0 の結果が遅れて届く。
	model, _ := m.Update(submitCheckMsg{check: SubmitCheck{Clean: true}, epoch: 0})
	m = model.(*chatModel)
	if submitted != 0 {
		t.Fatalf("stale check result must not trigger submit, got %d", submitted)
	}
	if m.submitChecking {
		t.Fatal("stale msg should not resurrect submitChecking")
	}
}

// チェック中の spinner tick はコマを進めて再アームする (submitChecking でも回る)。
func TestSubmitCheckSpinnerTicks(t *testing.T) {
	m := &chatModel{header: ChatHeader{SubmitCheck: func() SubmitCheck { return SubmitCheck{Clean: true} }}}
	m.startSubmitChecking()
	if !m.submitChecking {
		t.Fatal("startSubmitChecking should set submitChecking=true")
	}
	gen := m.spinGen
	before := m.spinnerFrame
	_, cmd := m.Update(spinnerTickMsg{gen: gen})
	if m.spinnerFrame != before+1 {
		t.Error("tick should advance the frame while submitChecking")
	}
	if cmd == nil {
		t.Error("tick should re-arm while submitChecking")
	}
	// チェック完了後の tick は止まる。
	m.submitChecking = false
	_, cmd2 := m.Update(spinnerTickMsg{gen: gen})
	if cmd2 != nil {
		t.Error("tick after submitChecking cleared should not re-arm")
	}
}
