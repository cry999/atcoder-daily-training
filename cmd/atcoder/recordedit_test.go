package main

import (
	"strings"
	"testing"

	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

// :record edit のロードフックは既存記録を Stat として返す (要件 066)。
func TestChatRecordEditLoad(t *testing.T) {
	chatRecordEnv(t)
	rec := chatRecordFunc(chatRecContest, chatRecTask, layout.ABC{})
	if _, err := rec([]string{"start"}); err != nil {
		t.Fatal(err)
	}
	if _, err := rec([]string{"ac", "ed", "score=2,3,2,3,1"}); err != nil {
		t.Fatal(err)
	}

	load := chatRecordEditLoadFunc(chatRecContest, chatRecTask, layout.ABC{})
	st, _, found, err := load()
	if err != nil || !found {
		t.Fatalf("load: found=%v err=%v", found, err)
	}
	if st.AC == nil || !*st.AC {
		t.Errorf("ac want true got %v", st.AC)
	}
	if st.Score.Knowledge != 2 || st.Score.Verify != 1 {
		t.Errorf("score not loaded: %+v", st.Score)
	}
}

// 記録が無ければ found=false (フォームは開かず案内する)。
func TestChatRecordEditLoad_Missing(t *testing.T) {
	chatRecordEnv(t)
	load := chatRecordEditLoadFunc(chatRecContest, chatRecTask, layout.ABC{})
	_, _, found, err := load()
	if err != nil {
		t.Fatalf("err=%v", err)
	}
	if found {
		t.Fatal("記録が無いのに found=true")
	}
}

// セーブフックは編集後 Stat を全置換保存し、クリアしたキーを落とす。
func TestChatRecordEditSave(t *testing.T) {
	chatRecordEnv(t)
	rec := chatRecordFunc(chatRecContest, chatRecTask, layout.ABC{})
	if _, err := rec([]string{"start"}); err != nil {
		t.Fatal(err)
	}
	if _, err := rec([]string{"ac", "score=2,3,2,3,1"}); err != nil {
		t.Fatal(err)
	}

	load := chatRecordEditLoadFunc(chatRecContest, chatRecTask, layout.ABC{})
	st, _, _, _ := load()
	// ac を未記録へ、editorial を true へ、knowledge を 0 へ。
	st.AC = nil
	st.Editorial = solvestat.BoolPtr(true)
	st.Score.Knowledge = 0

	save := chatRecordEditSaveFunc(chatRecContest, chatRecTask, layout.ABC{})
	lines, err := save(st)
	if err != nil {
		t.Fatal(err)
	}
	if len(lines) == 0 || !strings.Contains(lines[0], "更新しました") {
		t.Fatalf("lines=%v", lines)
	}

	got, found, err := solvestat.ReadFile(chatRecPath)
	if err != nil || !found {
		t.Fatalf("ReadFile: found=%v err=%v", found, err)
	}
	if got.AC != nil {
		t.Errorf("ac should be cleared, got %v", *got.AC)
	}
	if got.Editorial == nil || !*got.Editorial {
		t.Errorf("editorial want true got %v", got.Editorial)
	}
	if got.Score.Knowledge != 0 {
		t.Errorf("knowledge want 0 got %d", got.Score.Knowledge)
	}
	// started_at は温存されている。
	if got.StartedAt.IsZero() {
		t.Error("started_at が温存されていない")
	}
}

// CLI record edit: 記録が無ければ exit 1 で案内する。
func TestRecordEdit_NoRecord(t *testing.T) {
	chatRecordEnv(t)
	code, err := recordEdit([]string{chatRecContest, "--task", "d", "--layout", "abc"})
	if code != 1 || err == nil {
		t.Fatalf("code=%d err=%v", code, err)
	}
	if !strings.Contains(err.Error(), "記録がありません") && !strings.Contains(err.Error(), "solve-stat がありません") {
		t.Fatalf("unexpected err: %v", err)
	}
}

// CLI record edit: 記録はあるが非対話端末なのでフラグ経路を案内する (テストは非 TTY)。
func TestRecordEdit_NonInteractive(t *testing.T) {
	chatRecordEnv(t)
	rec := chatRecordFunc(chatRecContest, chatRecTask, layout.ABC{})
	if _, err := rec([]string{"start"}); err != nil {
		t.Fatal(err)
	}
	code, err := recordEdit([]string{chatRecContest, "--task", "d", "--layout", "abc"})
	if code != 1 || err == nil {
		t.Fatalf("code=%d err=%v", code, err)
	}
	if !strings.Contains(err.Error(), "対話端末") {
		t.Fatalf("unexpected err: %v", err)
	}
}
