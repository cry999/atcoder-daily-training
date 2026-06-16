package ui

import (
	"os/exec"
	"testing"
)

// Edit 未注入なら editFile は cmd を返さず「利用できません」を 1 行出す。
func TestEditFileNoHook(t *testing.T) {
	m := initialChatModel(ChatHeader{WatchPath: "a.py"}, fakeSpawn())
	if cmd := m.editFile(); cmd != nil {
		t.Error("editFile without Edit hook should return nil cmd")
	}
	if !hasInfo(m, "利用できません") {
		t.Errorf("expected unavailable message; msgs=%v", m.msgs)
	}
}

// 解答パスが空なら開けない旨を出す。
func TestEditFileNoPath(t *testing.T) {
	called := false
	m := initialChatModel(ChatHeader{Edit: func(string) EditPlan { called = true; return EditPlan{} }}, fakeSpawn())
	m.editFile()
	if called {
		t.Error("Edit hook should not be called when WatchPath is empty")
	}
	if !hasInfo(m, "不明") {
		t.Errorf("expected unknown-path message; msgs=%v", m.msgs)
	}
}

// remote ケース (Exec=nil): メッセージを 1 行出し cmd は返さない。渡されるパスは WatchPath。
func TestEditFileRemoteMessage(t *testing.T) {
	var gotPath string
	m := initialChatModel(ChatHeader{
		WatchPath: "exercise/abc457_d.py",
		Edit:      func(p string) EditPlan { gotPath = p; return EditPlan{Message: "nvim で開きました"} },
	}, fakeSpawn())
	if cmd := m.editFile(); cmd != nil {
		t.Error("remote (Exec=nil) should return nil cmd")
	}
	if gotPath != "exercise/abc457_d.py" {
		t.Errorf("Edit got path %q, want WatchPath", gotPath)
	}
	if !hasInfo(m, "nvim で開きました") {
		t.Errorf("expected the remote message; msgs=%v", m.msgs)
	}
}

// exec ケース (Exec 非 nil): tea.ExecProcess の cmd を返す (端末を奪う起動)。
func TestEditFileExecReturnsCmd(t *testing.T) {
	m := initialChatModel(ChatHeader{
		WatchPath: "a.py",
		Edit:      func(string) EditPlan { return EditPlan{Exec: exec.Command("true")} },
	}, fakeSpawn())
	if cmd := m.editFile(); cmd == nil {
		t.Error("exec plan (Exec!=nil) should return a non-nil tea.Cmd (ExecProcess)")
	}
}
