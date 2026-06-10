package extracase

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestListEmptyWhenNoDir(t *testing.T) {
	taskDir := t.TempDir()
	names, err := List(taskDir)
	if err != nil {
		t.Fatalf("List on missing dir should be nil error, got %v", err)
	}
	if len(names) != 0 {
		t.Errorf("expected empty, got %v", names)
	}
}

func TestSaveAutoSequencesAndLists(t *testing.T) {
	taskDir := t.TempDir()

	// 1 件目: 空 name → 01 採番。
	n1, err := Save(taskDir, "", []byte("5 3\n"), []byte("9\n"))
	if err != nil {
		t.Fatal(err)
	}
	if n1 != "01" {
		t.Errorf("first save should be 01, got %q", n1)
	}
	// 2 件目: 02 採番。
	n2, err := Save(taskDir, "", []byte("1\n"), []byte("1\n"))
	if err != nil {
		t.Fatal(err)
	}
	if n2 != "02" {
		t.Errorf("second save should be 02, got %q", n2)
	}

	names, err := List(taskDir)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(names, []string{"01", "02"}) {
		t.Errorf("List = %v, want [01 02]", names)
	}

	// 中身が書けているか。
	in, _ := os.ReadFile(filepath.Join(Dir(taskDir), "01.in"))
	if string(in) != "5 3\n" {
		t.Errorf("01.in = %q", in)
	}
}

func TestSaveEmptyExpectedAllowed(t *testing.T) {
	taskDir := t.TempDir()
	if _, err := Save(taskDir, "", []byte("x\n"), nil); err != nil {
		t.Fatalf("empty expected should be allowed: %v", err)
	}
	out, err := os.ReadFile(filepath.Join(Dir(taskDir), "01.out"))
	if err != nil || len(out) != 0 {
		t.Errorf("01.out should exist and be empty, got %q err=%v", out, err)
	}
}

func TestSaveRefusesOverwrite(t *testing.T) {
	taskDir := t.TempDir()
	if _, err := Save(taskDir, "mycase", []byte("a\n"), []byte("b\n")); err != nil {
		t.Fatal(err)
	}
	if _, err := Save(taskDir, "mycase", []byte("c\n"), []byte("d\n")); err == nil {
		t.Error("overwriting an existing case name should error")
	}
}

// 任意名 (非数値) のケースが在っても、数値の連番採番は壊れない。
func TestNextSeqIgnoresNonNumeric(t *testing.T) {
	taskDir := t.TempDir()
	if _, err := Save(taskDir, "edge", []byte("a\n"), []byte("b\n")); err != nil {
		t.Fatal(err)
	}
	n, err := Save(taskDir, "", []byte("c\n"), []byte("d\n"))
	if err != nil {
		t.Fatal(err)
	}
	if n != "01" {
		t.Errorf("numeric sequencing should ignore non-numeric names; got %q want 01", n)
	}
}
