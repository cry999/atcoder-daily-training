package ui

import (
	"os"
	"path/filepath"
	"testing"
)

// normalizeSampleRef は x プレフィックスで tests-extra に振り分け、数字を %02d 正規化する (要件 045)。
func TestNormalizeSampleRef(t *testing.T) {
	cases := []struct {
		ref      string
		wantDir  string
		wantName string
	}{
		{"1", "tests", "01"},
		{"01", "tests", "01"},
		{"12", "tests", "12"},
		{"x1", "tests-extra", "01"},
		{"x01", "tests-extra", "01"},
		{"X2", "tests-extra", "02"}, // 大文字 X も追加ケース
		{"", "tests", ""},           // 空参照は name 空 (呼び出し側で一覧扱い)
		{"abc", "tests", "abc"},     // 数字でない名前はそのまま (任意名の追加ケースに備える)
		{"x", "tests-extra", ""},    // x のみは名前空
	}
	for _, c := range cases {
		dir, name := normalizeSampleRef(c.ref)
		if dir != c.wantDir || name != c.wantName {
			t.Errorf("normalizeSampleRef(%q) = (%q, %q), want (%q, %q)", c.ref, dir, name, c.wantDir, c.wantName)
		}
	}
}

// listSampleCases は公式 (tests/) を昇順、追加 (tests-extra/) を x プレフィックスで後置する (要件 045)。
func TestListSampleCases(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests"), "02", "x", "y")
	writeCase(t, filepath.Join(taskDir, "tests"), "01", "a", "b")
	writeCase(t, filepath.Join(taskDir, "tests-extra"), "01", "p", "q")

	got := listSampleCases(taskDir)
	want := []string{"01", "02", "x01"}
	if !equalStrings(got, want) {
		t.Errorf("listSampleCases = %v, want %v", got, want)
	}
}

// ケースが 1 つも無ければ空 (サンプル未取得は正常)。
func TestListSampleCasesEmpty(t *testing.T) {
	if got := listSampleCases(t.TempDir()); len(got) != 0 {
		t.Errorf("listSampleCases (empty) = %v, want empty", got)
	}
}

// resolveSampleCase は .in/.out を行スライスに読み、表示 ID を返す。欠落は ok=false (要件 045)。
func TestResolveSampleCase(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests"), "01", "5 3\n1 2 3\n", "6\n")
	writeCase(t, filepath.Join(taskDir, "tests-extra"), "01", "9\n", "ok\n")

	// 公式: bare 数字 → 01 に正規化して解決。
	in, out, id, ok := resolveSampleCase(taskDir, "1")
	if !ok {
		t.Fatal("official case 1 should resolve")
	}
	if id != "01" {
		t.Errorf("official id = %q, want 01", id)
	}
	if !equalStrings(in, []string{"5 3", "1 2 3"}) {
		t.Errorf("official in = %v", in)
	}
	if !equalStrings(out, []string{"6"}) {
		t.Errorf("official out = %v", out)
	}

	// 追加: x プレフィックスで tests-extra を解決し、表示 ID は x01。
	_, _, xid, xok := resolveSampleCase(taskDir, "x1")
	if !xok || xid != "x01" {
		t.Errorf("extra case x1 = (id %q, ok %v), want (x01, true)", xid, xok)
	}

	// 欠落ケースは ok=false。
	if _, _, _, ok := resolveSampleCase(taskDir, "99"); ok {
		t.Error("missing case must not resolve")
	}
	// 空参照は ok=false (一覧は呼び出し側)。
	if _, _, _, ok := resolveSampleCase(taskDir, ""); ok {
		t.Error("empty ref must not resolve")
	}
}

// .out が無いケースも .in があれば解決し、expected は空 (検証なしで流せる)。
func TestResolveSampleCaseMissingOut(t *testing.T) {
	taskDir := t.TempDir()
	dir := filepath.Join(taskDir, "tests")
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "01.in"), []byte("1\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	in, out, id, ok := resolveSampleCase(taskDir, "01")
	if !ok || id != "01" {
		t.Fatalf("case with no .out should still resolve (id %q ok %v)", id, ok)
	}
	if !equalStrings(in, []string{"1"}) {
		t.Errorf("in = %v, want [1]", in)
	}
	if len(out) != 0 {
		t.Errorf("missing .out should give empty expected, got %v", out)
	}
}

// writeCase は dir/<name>.in と dir/<name>.out を書く (テスト用)。
func writeCase(t *testing.T, dir, name, in, out string) {
	t.Helper()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, name+".in"), []byte(in), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, name+".out"), []byte(out), 0o644); err != nil {
		t.Fatal(err)
	}
}
