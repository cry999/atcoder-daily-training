package watch

import (
	"context"
	"os"
	"path/filepath"
	"testing"
	"time"
)

// WaitForChange はファイルの mtime が変わると true を返す。
func TestWaitForChangeDetectsModification(t *testing.T) {
	p := filepath.Join(t.TempDir(), "sol.py")
	if err := os.WriteFile(p, []byte("a"), 0o644); err != nil {
		t.Fatal(err)
	}
	w := New(p, 20*time.Millisecond, 0)

	go func() {
		time.Sleep(40 * time.Millisecond)
		// fs の mtime 解像度に依らず確実に差を作るため Chtimes で未来時刻を打つ。
		future := time.Now().Add(2 * time.Second)
		_ = os.Chtimes(p, future, future)
	}()

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	if !w.WaitForChange(ctx) {
		t.Fatal("expected the modification to be detected")
	}
}

// 変更が無いまま ctx が done になったら false を返す (Ctrl+C 相当)。
func TestWaitForChangeReturnsFalseOnCtxCancel(t *testing.T) {
	p := filepath.Join(t.TempDir(), "sol.py")
	if err := os.WriteFile(p, []byte("a"), 0o644); err != nil {
		t.Fatal(err)
	}
	w := New(p, 20*time.Millisecond, 0)

	ctx, cancel := context.WithTimeout(context.Background(), 80*time.Millisecond)
	defer cancel()
	if w.WaitForChange(ctx) {
		t.Fatal("expected false when ctx is cancelled without a change")
	}
}

// 同一 mtime のままなら再実行をトリガしない (誤爆しない)。
func TestWaitForChangeNoFalsePositive(t *testing.T) {
	p := filepath.Join(t.TempDir(), "sol.py")
	if err := os.WriteFile(p, []byte("a"), 0o644); err != nil {
		t.Fatal(err)
	}
	w := New(p, 10*time.Millisecond, 0)

	// ファイルに触れない。短い待機で必ず ctx done → false。
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Millisecond)
	defer cancel()
	if w.WaitForChange(ctx) {
		t.Fatal("expected no change to be reported when the file is untouched")
	}
}

// Changed は非ブロッキングに 1 回 poll する。変化なしで false、変化ありで true を返し
// 基準を更新する (start のキー多重化待機が使う)。
func TestChanged(t *testing.T) {
	p := filepath.Join(t.TempDir(), "sol.py")
	if err := os.WriteFile(p, []byte("a"), 0o644); err != nil {
		t.Fatal(err)
	}
	w := New(p, 20*time.Millisecond, 0)

	if w.Changed() {
		t.Fatal("Changed() should be false right after New (no modification yet)")
	}
	future := time.Now().Add(2 * time.Second)
	if err := os.Chtimes(p, future, future); err != nil {
		t.Fatal(err)
	}
	if !w.Changed() {
		t.Fatal("Changed() should be true after the mtime changed")
	}
	// 基準が更新されているので、続けて呼ぶと false に戻る。
	if w.Changed() {
		t.Fatal("Changed() should be false again once the new mtime is the baseline")
	}
}
