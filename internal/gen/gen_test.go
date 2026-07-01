package gen

import (
	"bufio"
	"math/rand"
	"strconv"
	"strings"
	"testing"
)

func TestEvalNumber(t *testing.T) {
	cases := map[string]int64{
		"10^5":   100000,
		"10^9":   1000000000,
		"2*10^5": 200000,
		"200000": 200000,
		"-5":     -5,
		"3*10^2": 300,
		"1":      1,
	}
	for in, want := range cases {
		got, ok := evalNumber(in)
		if !ok || got != want {
			t.Errorf("evalNumber(%q) = %d,%v; want %d", in, got, ok, want)
		}
	}
	if _, ok := evalNumber("N"); ok {
		t.Errorf("evalNumber(N) should fail")
	}
}

func TestParseSpecScalarSeqRepeat(t *testing.T) {
	raw := Raw{
		InputFormat: "N M\nA_1 A_2 \\ldots A_N\nu_1 v_1\n:\nu_M v_M\n",
		Constraints: "1 \\leq N \\leq 2 \\times 10^5\n1 \\leq M \\leq N\n1 \\leq A_i \\leq 10^9\n1 \\leq u_i, v_i \\leq N\n",
	}
	sp, err := ParseSpec(raw)
	if err != nil {
		t.Fatalf("ParseSpec: %v", err)
	}
	if sp.Coverage != Full {
		t.Errorf("coverage = %v; want full. warnings=%v", sp.Coverage, sp.Warnings)
	}
	// 変数の範囲。
	if v := sp.Vars["N"]; v == nil || v.Max.Const != 200000 || !v.Max.Known {
		t.Errorf("N max wrong: %+v", v)
	}
	if v := sp.Vars["M"]; v == nil || v.Max.Ref != "N" {
		t.Errorf("M max should ref N: %+v", v)
	}
	if v := sp.Vars["A"]; v == nil || v.Max.Const != 1000000000 {
		t.Errorf("A max wrong: %+v", v)
	}
	// ブロック構成: scalar(N,M) / seq(A) / repeat(u,v)。
	if len(sp.Blocks) != 3 {
		t.Fatalf("blocks = %d (%+v); want 3", len(sp.Blocks), sp.Blocks)
	}
	if sp.Blocks[0].Kind != Scalar || len(sp.Blocks[0].Tokens) != 2 {
		t.Errorf("block0 not scalar N M: %+v", sp.Blocks[0])
	}
	if sp.Blocks[1].Kind != Seq || sp.Blocks[1].Var != "A" || sp.Blocks[1].Count.Ref != "N" {
		t.Errorf("block1 not seq A len N: %+v", sp.Blocks[1])
	}
	if sp.Blocks[2].Kind != Repeat || len(sp.Blocks[2].Tokens) != 2 || sp.Blocks[2].Count.Ref != "M" {
		t.Errorf("block2 not repeat u v count M: %+v", sp.Blocks[2])
	}
}

// TestGenerateRespectsConstraints は生成入力が形式・範囲を満たすことを確認する。
func TestGenerateRespectsConstraints(t *testing.T) {
	raw := Raw{
		InputFormat: "N M\nA_1 A_2 \\ldots A_N\nu_1 v_1\n:\nu_M v_M\n",
		Constraints: "1 \\leq N \\leq 100\n1 \\leq M \\leq N\n1 \\leq A_i \\leq 1000\n1 \\leq u_i, v_i \\leq N\n",
	}
	sp, err := ParseSpec(raw)
	if err != nil {
		t.Fatalf("ParseSpec: %v", err)
	}
	rng := rand.New(rand.NewSource(42))
	out, err := sp.Generate(rng, SizeRandom)
	if err != nil {
		t.Fatalf("Generate: %v", err)
	}
	sc := bufio.NewScanner(strings.NewReader(string(out)))
	sc.Buffer(make([]byte, 1<<20), 1<<20)

	// 1 行目: N M
	sc.Scan()
	nm := strings.Fields(sc.Text())
	if len(nm) != 2 {
		t.Fatalf("line1 = %q; want 'N M'", sc.Text())
	}
	n, _ := strconv.Atoi(nm[0])
	m, _ := strconv.Atoi(nm[1])
	if n < 1 || n > 100 {
		t.Errorf("N=%d out of [1,100]", n)
	}
	if m < 1 || m > n {
		t.Errorf("M=%d out of [1,N=%d]", m, n)
	}
	// 2 行目: 長さ N の配列、各要素 [1,1000]
	sc.Scan()
	arr := strings.Fields(sc.Text())
	if len(arr) != n {
		t.Fatalf("array len=%d; want N=%d", len(arr), n)
	}
	for _, s := range arr {
		a, _ := strconv.Atoi(s)
		if a < 1 || a > 1000 {
			t.Errorf("A element %d out of [1,1000]", a)
		}
	}
	// 続く M 行: u v ∈ [1,N]
	for i := 0; i < m; i++ {
		if !sc.Scan() {
			t.Fatalf("missing edge line %d", i)
		}
		uv := strings.Fields(sc.Text())
		if len(uv) != 2 {
			t.Fatalf("edge line = %q; want 'u v'", sc.Text())
		}
		for _, s := range uv {
			x, _ := strconv.Atoi(s)
			if x < 1 || x > n {
				t.Errorf("edge endpoint %d out of [1,N=%d]", x, n)
			}
		}
	}
	if sc.Scan() && strings.TrimSpace(sc.Text()) != "" {
		t.Errorf("unexpected trailing line %q", sc.Text())
	}
}

// TestGenerateDeterministicWithSeed は同じシードで同じ出力になることを確認する。
func TestGenerateDeterministicWithSeed(t *testing.T) {
	raw := Raw{
		InputFormat: "N\nA_1 A_2 \\ldots A_N\n",
		Constraints: "1 \\leq N \\leq 10\n1 \\leq A_i \\leq 100\n",
	}
	sp, _ := ParseSpec(raw)
	out1, _ := sp.Generate(rand.New(rand.NewSource(7)), SizeRandom)
	sp2, _ := ParseSpec(raw)
	out2, _ := sp2.Generate(rand.New(rand.NewSource(7)), SizeRandom)
	if string(out1) != string(out2) {
		t.Errorf("same seed produced different output:\n%s---\n%s", out1, out2)
	}
}

// TestGenerateSizeMax は --size max で上限が使われることを確認する。
func TestGenerateSizeMax(t *testing.T) {
	raw := Raw{
		InputFormat: "N\n",
		Constraints: "1 \\leq N \\leq 42\n",
	}
	sp, _ := ParseSpec(raw)
	out, _ := sp.Generate(rand.New(rand.NewSource(1)), SizeMax)
	if strings.TrimSpace(string(out)) != "42" {
		t.Errorf("size=max N = %q; want 42", strings.TrimSpace(string(out)))
	}
}

func TestParseSpecPartialCoverage(t *testing.T) {
	// K に制約が無い → 既定レンジ + 警告 + partial。
	raw := Raw{
		InputFormat: "N K\n",
		Constraints: "1 \\leq N \\leq 100\n",
	}
	sp, err := ParseSpec(raw)
	if err != nil {
		t.Fatalf("ParseSpec: %v", err)
	}
	if sp.Coverage != Partial {
		t.Errorf("coverage = %v; want partial", sp.Coverage)
	}
	if len(sp.Warnings) == 0 {
		t.Errorf("expected a warning for K")
	}
}

func TestParseSpecString(t *testing.T) {
	raw := Raw{
		InputFormat: "S\n",
		Constraints: "1 \\leq |S| \\leq 20\nS consists of lowercase English letters\n",
	}
	sp, err := ParseSpec(raw)
	if err != nil {
		t.Fatalf("ParseSpec: %v", err)
	}
	if v := sp.Vars["S"]; v == nil || v.Type != String {
		t.Fatalf("S should be a string var: %+v", sp.Vars["S"])
	}
	if len(sp.Blocks) != 1 || sp.Blocks[0].Kind != Str {
		t.Fatalf("expected one Str block: %+v", sp.Blocks)
	}
	out, _ := sp.Generate(rand.New(rand.NewSource(3)), SizeRandom)
	s := strings.TrimSpace(string(out))
	if len(s) < 1 || len(s) > 20 {
		t.Errorf("string len=%d out of [1,20]: %q", len(s), s)
	}
	for _, r := range s {
		if r < 'a' || r > 'z' {
			t.Errorf("char %q not lowercase", r)
		}
	}
}

func TestParseSpecEmpty(t *testing.T) {
	if _, err := ParseSpec(Raw{}); err == nil {
		t.Errorf("empty raw should error")
	}
}

// TestParseSpecAbsoluteValue は |v| ≤ C を文字列長でなく整数の絶対値 (-C..C) として
// 扱うことを確認する (文字列キーワードが無いとき)。AtCoder 頻出パターン。
func TestParseSpecAbsoluteValue(t *testing.T) {
	raw := Raw{
		InputFormat: "N\nA_1 A_2 \\ldots A_N\n",
		Constraints: "1 \\leq N \\leq 5\n|A_i| \\leq 100\n",
	}
	sp, err := ParseSpec(raw)
	if err != nil {
		t.Fatalf("ParseSpec: %v", err)
	}
	a := sp.Vars["A"]
	if a == nil || a.Type != Int {
		t.Fatalf("A should stay an int var: %+v", a)
	}
	if a.Min.Const != -100 || a.Max.Const != 100 {
		t.Fatalf("A abs bounds wrong: min=%+v max=%+v (want -100..100)", a.Min, a.Max)
	}
	// 生成値に負が出うる (範囲 [-100,100] を守る)。
	sawNeg := false
	for seed := int64(0); seed < 20 && !sawNeg; seed++ {
		out, _ := sp.Generate(rand.New(rand.NewSource(seed)), SizeRandom)
		for _, line := range strings.Split(strings.TrimSpace(string(out)), "\n") {
			for _, tok := range strings.Fields(line) {
				v, err := strconv.Atoi(tok)
				if err != nil {
					continue
				}
				if v < -100 || v > 100 {
					t.Fatalf("value %d out of [-100,100]", v)
				}
				if v < 0 {
					sawNeg = true
				}
			}
		}
	}
	if !sawNeg {
		t.Errorf("expected some negative A value across seeds (abs-value range)")
	}
}

// TestParseSpecUpperOnlyWarns は上限だけ取れた変数を partial + 警告にすることを確認する。
func TestParseSpecUpperOnlyWarns(t *testing.T) {
	raw := Raw{
		InputFormat: "N\n",
		Constraints: "N \\leq 100\n", // 下限が無い
	}
	sp, err := ParseSpec(raw)
	if err != nil {
		t.Fatalf("ParseSpec: %v", err)
	}
	if sp.Coverage != Partial {
		t.Errorf("upper-only bound should be partial; warnings=%v", sp.Warnings)
	}
	if sp.Vars["N"].Max.Const != 100 {
		t.Errorf("N max should be 100: %+v", sp.Vars["N"].Max)
	}
}
