package runner

import (
	"bufio"
	"os"
	"path/filepath"
	"testing"
)

// StartChat は stdout と stderr を 1 本のストリームに束ねて返し、子が出した順を保つこと。
// 別々の pipe を並行に読んでいた頃は DEBUG (stdout) と traceback (stderr) が互い違いに
// 並ぶことがあった。統合により write 順がそのまま読める。
func TestStartChatMergesStdoutStderrInOrder(t *testing.T) {
	py, err := NewPython()
	if err != nil {
		t.Skipf("python が見つからないため skip: %v", err)
	}

	// stdout と stderr を交互に出す子。PYTHONUNBUFFERED は StartChat が付けるので
	// 各 print はその場で同じ pipe に書かれ、プログラム順が保たれる。
	src := `import sys
print("out1")
print("err1", file=sys.stderr)
print("out2")
print("err2", file=sys.stderr)
print("out3")
`
	dir := t.TempDir()
	path := filepath.Join(dir, "main.py")
	if err := os.WriteFile(path, []byte(src), 0o644); err != nil {
		t.Fatal(err)
	}

	h, err := py.StartChat(path, nil)
	if err != nil {
		t.Fatalf("StartChat: %v", err)
	}
	defer h.Kill()

	var got []string
	sc := bufio.NewScanner(h.Stdout)
	for sc.Scan() {
		got = append(got, sc.Text())
	}
	h.Wait()

	want := []string{"out1", "err1", "out2", "err2", "out3"}
	if len(got) != len(want) {
		t.Fatalf("merged lines = %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("merged order = %v, want %v (line %d differs)", got, want, i)
		}
	}

	// Stderr は統合済みなので即 EOF (別ストリームは無い)。
	sc2 := bufio.NewScanner(h.Stderr)
	if sc2.Scan() {
		t.Errorf("Stderr should be empty after merge, got %q", sc2.Text())
	}
}
