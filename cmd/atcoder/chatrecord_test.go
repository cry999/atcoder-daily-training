package main

import (
	"strings"
	"testing"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

// chatRecordEnv は空の config と一時 CWD を用意する。auto レイアウトは abc<NNN> を ABC
// (abc/<num>/<letter>.py) に解決するので、解答パスは決定的 (abc/457/d.py)。
func chatRecordEnv(t *testing.T) {
	t.Helper()
	t.Setenv("XDG_CONFIG_HOME", t.TempDir())
	t.Chdir(t.TempDir())
}

const chatRecContest, chatRecTask = "abc457", "abc457_d"
const chatRecPath = "abc/457/d.py"

// :record start → started_at を刻み、solve-stat ブロックを新規作成する。
func TestChatRecordFunc_Start(t *testing.T) {
	chatRecordEnv(t)
	rec := chatRecordFunc(chatRecContest, chatRecTask)

	lines, err := rec([]string{"start"})
	if err != nil {
		t.Fatal(err)
	}
	if len(lines) != 1 || !strings.Contains(lines[0], "計測を開始しました") {
		t.Fatalf("lines=%v", lines)
	}
	st, found, err := solvestat.ReadFile(chatRecPath)
	if err != nil || !found {
		t.Fatalf("ReadFile: found=%v err=%v", found, err)
	}
	if st.StartedAt.IsZero() {
		t.Fatal("started_at が刻まれていない")
	}
	// 再実行は冪等 (継続中)。
	lines2, _ := rec([]string{"start"})
	if len(lines2) != 1 || !strings.Contains(lines2[0], "継続中") {
		t.Fatalf("再 start lines=%v", lines2)
	}
}

// :record ac ed score=… → 非対話フラグを solve-stat へ書き戻し、要約行を返す。
func TestChatRecordFunc_RecordFlags(t *testing.T) {
	chatRecordEnv(t)
	rec := chatRecordFunc(chatRecContest, chatRecTask)
	if _, err := rec([]string{"start"}); err != nil {
		t.Fatal(err)
	}

	lines, err := rec([]string{"ac", "ed", "score=2,3,2,3,1"})
	if err != nil {
		t.Fatal(err)
	}
	joined := strings.Join(lines, "\n")
	if !strings.Contains(joined, "記録しました") || !strings.Contains(joined, "ac=true  editorial=true") {
		t.Fatalf("lines=%v", lines)
	}
	if !strings.Contains(joined, "score  k=2 t=3 c=2 i=3 v=1") {
		t.Fatalf("score 行が無い: %v", lines)
	}
	st, _, _ := solvestat.ReadFile(chatRecPath)
	if st.AC == nil || !*st.AC || st.Editorial == nil || !*st.Editorial {
		t.Fatalf("ac/editorial 未記録: %+v", st)
	}
	if st.Score.Knowledge != 2 || st.Score.Verify != 1 || st.SolvedAt.IsZero() {
		t.Fatalf("score/solved_at 未記録: %+v", st)
	}
}

// 引数なし :record は書き込まず現在値だけ返す。記録前は「まだ記録がありません」。
func TestChatRecordFunc_ShowNoWrite(t *testing.T) {
	chatRecordEnv(t)
	rec := chatRecordFunc(chatRecContest, chatRecTask)

	// 記録前 (ファイルも無い) の表示。
	lines, err := rec(nil)
	if err != nil {
		t.Fatal(err)
	}
	if len(lines) != 1 || !strings.Contains(lines[0], "まだ記録がありません") {
		t.Fatalf("空表示 lines=%v", lines)
	}

	// start → ac 記録 → 引数なし表示は書き込まず現在値を返す。
	if _, err := rec([]string{"start"}); err != nil {
		t.Fatal(err)
	}
	if _, err := rec([]string{"ac"}); err != nil {
		t.Fatal(err)
	}
	before, _, _ := solvestat.ReadFile(chatRecPath)
	show, _ := rec(nil)
	if strings.Join(show, "\n") == "" || !strings.Contains(strings.Join(show, "\n"), "ac=true") {
		t.Fatalf("show lines=%v", show)
	}
	after, _, _ := solvestat.ReadFile(chatRecPath)
	if !after.SolvedAt.Equal(before.SolvedAt) {
		t.Fatal("引数なし :record が書き込んでしまった (solved_at が変化)")
	}
}

// stop は解答ファイルが無ければ error (先に start を促す)。
func TestChatRecordFunc_StopMissing(t *testing.T) {
	chatRecordEnv(t)
	rec := chatRecordFunc(chatRecContest, chatRecTask)
	if _, err := rec([]string{"stop"}); err == nil {
		t.Fatal("want error for stop before start")
	}
}

// 不正トークンは error (chat は err 行で吸収)。
func TestChatRecordFunc_BadTokens(t *testing.T) {
	chatRecordEnv(t)
	rec := chatRecordFunc(chatRecContest, chatRecTask)
	if _, err := rec([]string{"start"}); err != nil {
		t.Fatal(err)
	}
	cases := [][]string{
		{"ac", "noac"},      // 相反 bool
		{"score=1,2,3"},     // 値数不足
		{"score=9,9,9,9,9"}, // 範囲外
		{"time=nonsense"},   // duration 不正
		{"bogus"},           // 未知トークン
	}
	for _, args := range cases {
		if _, err := rec(args); err == nil {
			t.Fatalf("want error for %v", args)
		}
	}
}
