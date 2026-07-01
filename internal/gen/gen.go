// Package gen は問題の制約 (Constraints) と入力形式 (Input) の生テキストを
// 構造解析 (Spec) し、それを満たすランダム入力を生成する (要件 060)。
//
// 方針はベストエフォート即生成 (ADR 0008): 認識できた制約でその場で入力を吐き、
// 取りこぼした変数は既定レンジ + 警告で埋める。自然言語の構造的制約 (順列・連結
// グラフ・単調列など) は理解できず、その旨を警告に落として coverage=partial とする。
// 出力の正しさは保証しない下準備ツールで、判定 (testexec) とは疎に保つ。
package gen

import (
	"fmt"
	"math/rand"
	"regexp"
	"strconv"
	"strings"
)

// VarType は認識した変数の種別。
type VarType int

const (
	Int VarType = iota
	String
)

// Bound は変数の下限 / 上限、または配列長 / 反復回数を表す。Ref が空なら定数
// (Const)、非空なら他変数の生成値 (+Offset) を実行時に解決する。Known=false は
// 制約が取れず既定値で埋めたことを示す (警告対象)。
type Bound struct {
	Ref    string
	Const  int64
	Offset int64
	Known  bool
}

func constBound(v int64) Bound   { return Bound{Const: v, Known: true} }
func refBound(name string) Bound { return Bound{Ref: name, Known: true} }

// Var は認識した変数の型と範囲。添字変数 (A_i) は基底名 (A) に畳む。String 型では
// Min/Max を文字列長として解釈する。
type Var struct {
	Name    string
	Type    VarType
	Min     Bound
	Max     Bound
	Charset string
}

// BlockKind は入力形式の 1 まとまりの種別。
type BlockKind int

const (
	Scalar BlockKind = iota // 1 行のスカラ列 (N M K)
	Seq                     // 配列 (A_1 .. A_N)
	Repeat                  // 行テンプレートの反復 (M 行の u_i v_i)
	Str                     // 単一文字列 (S)
)

// Layout は Seq の並べ方。
type Layout int

const (
	Row Layout = iota // 1 行に空白区切り
	Col               // 1 要素 1 行
)

// Block は入力形式の 1 まとまり。
type Block struct {
	Kind   BlockKind
	Tokens []string // Scalar/Repeat: 行に並ぶ変数の基底名
	Var    string   // Seq/Str: 配列 / 文字列の基底名
	Count  Bound    // Seq/Repeat: 配列長 / 反復行数
	Layout Layout   // Seq
}

// Coverage は認識の網羅度。
type Coverage int

const (
	Full Coverage = iota
	Partial
)

func (c Coverage) String() string {
	if c == Partial {
		return "partial"
	}
	return "full"
}

// Spec は生成器が直接使う中間表現 (永続化しない)。
type Spec struct {
	Vars     map[string]*Var
	Blocks   []Block
	Warnings []string
	Coverage Coverage
}

// SizeMode は生成する入力のサイズ方針。
type SizeMode int

const (
	SizeRandom SizeMode = iota // 範囲内で無作為
	SizeMax                    // 全変数・全長を上限に (TLE 探索用)
	SizeMin                    // 下限
)

// ParseSizeMode は --size フラグの値を SizeMode に変換する。
func ParseSizeMode(s string) (SizeMode, error) {
	switch s {
	case "", "random":
		return SizeRandom, nil
	case "max":
		return SizeMax, nil
	case "min":
		return SizeMin, nil
	default:
		return 0, fmt.Errorf("unknown --size %q (want random|max|min)", s)
	}
}

// 既定レンジ (制約が取れなかった変数に使う)。
const (
	defaultIntMin  = 1
	defaultIntMax  = 1_000_000_000
	defaultStrMin  = 1
	defaultStrMax  = 100_000
	defaultCharset = "abcdefghijklmnopqrstuvwxyz"
	// genCountCap は配列長 / 反復回数の上限。制約の取りこぼしで length 変数が
	// 既定 1e9 になっても爆発的な出力を出さないための安全弁。
	genCountCap = 200_000
)

// ParseSpec は生テキスト (Raw) から Spec を組む。認識できない部分は警告に落とし、
// 変数が 1 つも取れなければ error を返す (生成不能)。
func ParseSpec(raw Raw) (*Spec, error) {
	sp := &Spec{Vars: map[string]*Var{}, Coverage: Full}

	// 1. 制約を解析して変数の型・範囲を先に確定させる。
	// 文字列キーワード (文字列 / lowercase 等) の有無で `|v|` を「文字列長」と
	// 「整数の絶対値」のどちらに解釈するかを切り替える (bug: |A_i| ≤ C の誤判定回避)。
	hasStringKw := stringKwRe.MatchString(raw.Constraints)
	parseConstraints(raw.Constraints, sp, hasStringKw)

	// 2. 入力形式を解析してブロック列を組む。未知トークンはここで既定 Var を作る。
	blocks := parseFormat(raw.InputFormat, sp)
	sp.Blocks = blocks

	if len(sp.Vars) == 0 || len(sp.Blocks) == 0 {
		return nil, fmt.Errorf("could not parse input format (no variables recognized)")
	}

	// 3. 取りこぼし (既定レンジで埋めた変数・構造的制約) を警告に反映。
	for _, name := range sortedVarNames(sp.Vars) {
		v := sp.Vars[name]
		if !v.Min.Known || !v.Max.Known {
			sp.Warnings = append(sp.Warnings,
				fmt.Sprintf("variable %s: no constraint found; defaulted range", v.Name))
			sp.Coverage = Partial
		}
	}
	for _, w := range structuralWarnings(raw.Constraints) {
		sp.Warnings = append(sp.Warnings, w)
		sp.Coverage = Partial
	}
	return sp, nil
}

// --- 制約解析 -------------------------------------------------------------

var (
	// 数値トークン (10^9, 2*10^5, 200000, -5 など、正規化後)。
	numRe = regexp.MustCompile(`^-?\d+(\*\d+)?(\^\d+)?$`)
	// 文字列変数を示すキーワード。これがあるとき `|v|` を文字列長として解釈する
	// (無ければ整数の絶対値 |v| ≤ C = -C ≤ v ≤ C とみなす)。
	stringKwRe = regexp.MustCompile(`(?i)文字列|英小文字|英大文字|大文字|小文字|string|lowercase|uppercase|consists? of|consisting of`)
	// 構造的制約のキーワード (理解できないので警告するだけ)。
	structuralKeywords = []struct {
		re   *regexp.Regexp
		note string
	}{
		{regexp.MustCompile(`(?i)permutation|順列`), `a "permutation" constraint was found but is not enforced`},
		{regexp.MustCompile(`(?i)connected|連結`), `a "connected graph" constraint was found but is not enforced`},
		{regexp.MustCompile(`(?i)\btree\b|木である|木`), `a "tree" constraint was found but is not enforced`},
		{regexp.MustCompile(`(?i)distinct|相異なる|異なる`), `a "distinct values" constraint was found but is not enforced`},
		{regexp.MustCompile(`(?i)strictly|狭義単調|単調増加|increasing`), `a "monotonic" constraint was found but is not enforced`},
	}
)

// normalizeConstraint は LaTeX / 記号ゆれを吸収して比較しやすい形に均す。
func normalizeConstraint(s string) string {
	r := strings.NewReplacer(
		`\leq`, "<=", `\le`, "<=", "≤", "<=", "≦", "<=",
		`\geq`, ">=", `\ge`, ">=", "≥", ">=", "≧", ">=",
		`\lt`, "<", `\gt`, ">",
		`\times`, "*", "×", "*", `\cdot`, "*", "·", "*",
		`\ `, " ", `\,`, " ", `\;`, " ", `\!`, "",
		`\(`, " ", `\)`, " ", `\[`, " ", `\]`, " ",
		`\{`, "", `\}`, "", "{", "", "}", "",
		"$", " ", "＝", "=", "，", ",", "、", ",",
	)
	return r.Replace(s)
}

// parseConstraints は制約テキストを 1 行ずつ見て、比較チェインから変数の範囲を拾う。
// stringMode が真なら `|v|` を文字列長、偽なら整数の絶対値として解釈する。
func parseConstraints(text string, sp *Spec, stringMode bool) {
	for _, rawLine := range strings.Split(text, "\n") {
		line := normalizeConstraint(rawLine)
		// ">=" を "<=" チェインに反転して扱いを一本化する (a >= b → b <= a)。
		if strings.Contains(line, ">=") || (strings.Contains(line, ">") && !strings.Contains(line, "<")) {
			line = reverseCompare(line)
		}
		parts := splitCompare(line)
		if len(parts) < 2 {
			continue
		}
		applyCompareChain(parts, sp, stringMode)
	}
}

// splitCompare は "a <= b <= c" を ["a","b","c"] に割る (<= と < の両方で切る)。
func splitCompare(line string) []string {
	tmp := strings.ReplaceAll(line, "<=", "\x00")
	tmp = strings.ReplaceAll(tmp, "<", "\x00")
	var out []string
	for _, p := range strings.Split(tmp, "\x00") {
		out = append(out, strings.TrimSpace(p))
	}
	return out
}

// reverseCompare は ">=" / ">" を含む式を左右反転して "<=" 主体に直す。
// 単純な 2 項 / 3 項の連鎖だけを対象にする。
func reverseCompare(line string) string {
	norm := strings.ReplaceAll(line, ">=", "\x00")
	norm = strings.ReplaceAll(norm, ">", "\x00")
	parts := strings.Split(norm, "\x00")
	for i := range parts {
		parts[i] = strings.TrimSpace(parts[i])
	}
	// 反転して <= で連結。
	for i, j := 0, len(parts)-1; i < j; i, j = i+1, j-1 {
		parts[i], parts[j] = parts[j], parts[i]
	}
	return strings.Join(parts, " <= ")
}

// applyCompareChain は分割済みの比較チェインを変数範囲に反映する。
// [lo, var, hi] / [var, hi] / [lo, var] の 3 形をカバーし、var スロットは
// カンマ区切りの複数変数 (u_i, v_i) にも対応する。
func applyCompareChain(parts []string, sp *Spec, stringMode bool) {
	// 各要素が数値かどうか。
	isNum := make([]bool, len(parts))
	for i, p := range parts {
		isNum[i] = numRe.MatchString(strings.ReplaceAll(p, " ", ""))
	}

	switch len(parts) {
	case 3:
		lo, mid, hi := parts[0], parts[1], parts[2]
		if isNum[0] && !isNum[1] {
			// lo <= var <= hi (hi は数値 or 変数)。
			assignVars(mid, &loHi{lo: lo, hi: hi}, sp, stringMode)
		}
	case 2:
		a, b := parts[0], parts[1]
		if !isNum[0] && b != "" {
			// var <= hi
			assignVars(a, &loHi{hi: b}, sp, stringMode)
		} else if isNum[0] && !isNum[1] {
			// lo <= var
			assignVars(b, &loHi{lo: a}, sp, stringMode)
		}
	}
}

type loHi struct{ lo, hi string }

// assignVars は "u_i, v_i" のような複数変数スロットへ範囲を割り当てる。
// `|v|` トークンは stringMode で文字列長 (S) / 整数の絶対値 (A_i) を切り替える。
func assignVars(slot string, lh *loHi, sp *Spec, stringMode bool) {
	for _, tok := range strings.Split(slot, ",") {
		tok = strings.TrimSpace(tok)
		if tok == "" {
			continue
		}
		base, isBar := baseName(tok)
		if base == "" {
			continue
		}
		v := ensureVar(sp, base)
		switch {
		case isBar && stringMode:
			// |S| ≤ C: 文字列長の制約。
			v.Type = String
			if v.Charset == "" {
				v.Charset = defaultCharset
			}
			applyLoHi(v, lh)
		case isBar:
			// |v| ≤ C: 整数の絶対値。-C ≤ v ≤ C とみなす (AtCoder 頻出)。
			// 上限が変数参照の場合 (|A_i| ≤ N 等) はきれいに符号反転できないので、
			// Max だけ入れて Min は既定 (Known=false → 警告) に委ねる。
			if b, ok := parseBound(lh.hi); ok {
				v.Max = b
				if b.Ref == "" {
					v.Min = constBound(-b.Const)
				}
			}
		default:
			applyLoHi(v, lh)
		}
	}
}

// applyLoHi は制約チェインの下限 / 上限を Var に反映する (取れた側だけ)。
func applyLoHi(v *Var, lh *loHi) {
	if lh.lo != "" {
		if b, ok := parseBound(lh.lo); ok {
			v.Min = b
		}
	}
	if lh.hi != "" {
		if b, ok := parseBound(lh.hi); ok {
			v.Max = b
		}
	}
}

// baseName は変数トークンから基底名を取り出す。|S| は長さ制約とみなし isLen=true。
// A_i / A_{i,j} は添字を落として A に畳む。
func baseName(tok string) (name string, isLen bool) {
	tok = strings.TrimSpace(tok)
	if strings.HasPrefix(tok, "|") && strings.HasSuffix(tok, "|") && len(tok) >= 2 {
		tok = strings.Trim(tok, "|")
		isLen = true
	}
	if i := strings.IndexByte(tok, '_'); i >= 0 {
		tok = tok[:i]
	}
	tok = strings.TrimSpace(tok)
	// 識別子として妥当な先頭のみ採用 (数式の破片を弾く)。
	if tok == "" || !isIdentStart(tok[0]) {
		return "", isLen
	}
	return tok, isLen
}

func isIdentStart(b byte) bool {
	return (b >= 'A' && b <= 'Z') || (b >= 'a' && b <= 'z')
}

// parseBound は制約の右辺 / 左辺を Bound に変換する。数値なら定数、識別子なら
// 変数参照 (N-1 のようなオフセットも拾う)。
func parseBound(s string) (Bound, bool) {
	s = strings.ReplaceAll(s, " ", "")
	if v, ok := evalNumber(s); ok {
		return constBound(v), true
	}
	// N-1 / N+1 のような単純オフセット付き参照。
	off := int64(0)
	ref := s
	if i := strings.IndexAny(s, "+-"); i > 0 {
		if n, err := strconv.ParseInt(s[i:], 10, 64); err == nil {
			off = n
			ref = s[:i]
		}
	}
	base, _ := baseName(ref)
	if base == "" {
		return Bound{}, false
	}
	b := refBound(base)
	b.Offset = off
	return b, true
}

// evalNumber は "10^9" / "2*10^5" / "200000" / "-5" を int64 に評価する。
func evalNumber(s string) (int64, bool) {
	s = strings.ReplaceAll(s, " ", "")
	if s == "" {
		return 0, false
	}
	neg := false
	if strings.HasPrefix(s, "-") {
		neg = true
		s = s[1:]
	}
	prod := int64(1)
	for _, factor := range strings.Split(s, "*") {
		if factor == "" {
			return 0, false
		}
		var val int64
		if i := strings.IndexByte(factor, '^'); i >= 0 {
			base, err1 := strconv.ParseInt(factor[:i], 10, 64)
			exp, err2 := strconv.ParseInt(factor[i+1:], 10, 64)
			if err1 != nil || err2 != nil || exp < 0 || exp > 18 {
				return 0, false
			}
			val = 1
			for k := int64(0); k < exp; k++ {
				val *= base
			}
		} else {
			v, err := strconv.ParseInt(factor, 10, 64)
			if err != nil {
				return 0, false
			}
			val = v
		}
		prod *= val
	}
	if neg {
		prod = -prod
	}
	return prod, true
}

func structuralWarnings(constraints string) []string {
	var out []string
	for _, k := range structuralKeywords {
		if k.re.MatchString(constraints) {
			out = append(out, k.note)
		}
	}
	return out
}

// --- 入力形式解析 ---------------------------------------------------------

var ellipsisRe = regexp.MustCompile(`\\dots|\\ldots|\\cdots|\.\.\.|…|⋯|\\dotsc`)

// parseFormat は入力形式の <pre> テキストを行ごとに見てブロック列を組む。
func parseFormat(text string, sp *Spec) []Block {
	lines := nonEmptyLines(text)
	var blocks []Block
	for i := 0; i < len(lines); i++ {
		line := lines[i]

		// 縦の反復 / 縦の配列: 次行以降に ":" 継続と _<var> 終端があるパターン。
		if adv, blk, ok := parseVerticalRepeat(lines, i, sp); ok {
			blocks = append(blocks, blk)
			i = adv
			continue
		}

		// 横の配列: A_1 A_2 ... A_N
		if ellipsisRe.MatchString(line) {
			if blk, ok := parseHorizontalSeq(line, sp); ok {
				blocks = append(blocks, blk)
				continue
			}
		}

		// スカラ行 (N M K など、または単一文字列 S)。
		if blk, ok := parseScalarLine(line, sp); ok {
			blocks = append(blocks, blk)
		}
	}
	return blocks
}

// parseVerticalRepeat は
//
//	u_1 v_1
//	:
//	u_M v_M
//
// または
//
//	A_1
//	:
//	A_N
//
// のパターンを 1 ブロックに畳む。i は開始行、返り値 adv は最終消費行。
func parseVerticalRepeat(lines []string, i int, sp *Spec) (adv int, blk Block, ok bool) {
	first := fields(lines[i])
	if len(first) == 0 || !allSubscript(first, "1") {
		return 0, Block{}, false
	}
	// 継続マーカー (":" や "⋮") を探す。
	j := i + 1
	if j >= len(lines) || !isContinuation(lines[j]) {
		return 0, Block{}, false
	}
	// マーカーの次に終端行 (_<var>) があるはず。
	k := j + 1
	if k >= len(lines) {
		return 0, Block{}, false
	}
	last := fields(lines[k])
	if len(last) != len(first) {
		return 0, Block{}, false
	}
	countVar := subscriptOf(last[0])
	if countVar == "" {
		return 0, Block{}, false
	}
	bases := baseTokens(first)
	for _, b := range bases {
		ensureVar(sp, b)
	}
	count := boundFromSubscript(countVar)
	if len(bases) == 1 {
		// 縦の配列 (1 トークン/行)。
		return k, Block{Kind: Seq, Var: bases[0], Count: count, Layout: Col}, true
	}
	return k, Block{Kind: Repeat, Tokens: bases, Count: count}, true
}

// parseHorizontalSeq は "A_1 A_2 ... A_N" を Seq(row) に。
func parseHorizontalSeq(line string, sp *Spec) (Block, bool) {
	toks := fields(line)
	var base, lenVar string
	for _, t := range toks {
		if ellipsisRe.MatchString(t) {
			continue
		}
		b := subscriptBase(t)
		if b == "" {
			continue
		}
		if base == "" {
			base = b
		}
		lenVar = subscriptOf(t) // 最後に見た添字を長さ変数候補にする
	}
	if base == "" || lenVar == "" || isNumeric(lenVar) {
		return Block{}, false
	}
	ensureVar(sp, base)
	return Block{Kind: Seq, Var: base, Count: boundFromSubscript(lenVar), Layout: Row}, true
}

// parseScalarLine は "N M K" や単一 "S" をスカラ / 文字列ブロックに。
func parseScalarLine(line string, sp *Spec) (Block, bool) {
	toks := fields(line)
	var bases []string
	for _, t := range toks {
		b := subscriptBase(t)
		if b == "" {
			continue
		}
		bases = append(bases, b)
		ensureVar(sp, b)
	}
	if len(bases) == 0 {
		return Block{}, false
	}
	// 単一の文字列変数なら Str ブロック。
	if len(bases) == 1 && sp.Vars[bases[0]].Type == String {
		return Block{Kind: Str, Var: bases[0]}, true
	}
	return Block{Kind: Scalar, Tokens: bases}, true
}

// --- 生成 -----------------------------------------------------------------

// Generate は size モードに従い spec を満たす入力を 1 つ返す。
func (s *Spec) Generate(rng *rand.Rand, size SizeMode) ([]byte, error) {
	values := map[string]int64{} // スカラ変数の生成値 (参照解決に使う)
	var b strings.Builder

	resolve := func(bd Bound) int64 {
		if bd.Ref != "" {
			if v, ok := values[bd.Ref]; ok {
				return v + bd.Offset
			}
			return defaultIntMax // 参照先未生成 (通常起きない)
		}
		return bd.Const
	}
	genInt := func(v *Var) int64 {
		lo, hi := resolve(v.Min), resolve(v.Max)
		return sampleInt(rng, lo, hi, size)
	}
	genCount := func(bd Bound) int64 {
		n := resolve(bd)
		if n < 0 {
			n = 0
		}
		if n > genCountCap {
			n = genCountCap
		}
		return n
	}

	for _, blk := range s.Blocks {
		switch blk.Kind {
		case Scalar:
			parts := make([]string, len(blk.Tokens))
			for i, name := range blk.Tokens {
				v := s.Vars[name]
				x := genInt(v)
				values[name] = x
				parts[i] = strconv.FormatInt(x, 10)
			}
			b.WriteString(strings.Join(parts, " "))
			b.WriteByte('\n')
		case Seq:
			v := s.Vars[blk.Var]
			n := genCount(blk.Count)
			parts := make([]string, n)
			for i := int64(0); i < n; i++ {
				parts[i] = strconv.FormatInt(sampleInt(rng, resolve(v.Min), resolve(v.Max), size), 10)
			}
			if blk.Layout == Col {
				for _, p := range parts {
					b.WriteString(p)
					b.WriteByte('\n')
				}
			} else {
				b.WriteString(strings.Join(parts, " "))
				b.WriteByte('\n')
			}
		case Repeat:
			n := genCount(blk.Count)
			for i := int64(0); i < n; i++ {
				parts := make([]string, len(blk.Tokens))
				for j, name := range blk.Tokens {
					v := s.Vars[name]
					parts[j] = strconv.FormatInt(sampleInt(rng, resolve(v.Min), resolve(v.Max), size), 10)
				}
				b.WriteString(strings.Join(parts, " "))
				b.WriteByte('\n')
			}
		case Str:
			v := s.Vars[blk.Var]
			lo, hi := resolve(v.Min), resolve(v.Max)
			ln := sampleInt(rng, lo, hi, size)
			if ln > genCountCap {
				ln = genCountCap
			}
			if ln < 1 {
				ln = 1
			}
			charset := v.Charset
			if charset == "" {
				charset = defaultCharset
			}
			buf := make([]byte, ln)
			for i := range buf {
				buf[i] = charset[rng.Intn(len(charset))]
			}
			b.Write(buf)
			b.WriteByte('\n')
		}
	}
	return []byte(b.String()), nil
}

func sampleInt(rng *rand.Rand, lo, hi int64, size SizeMode) int64 {
	if hi < lo {
		hi = lo
	}
	switch size {
	case SizeMax:
		return hi
	case SizeMin:
		return lo
	default:
		span := hi - lo
		if span <= 0 {
			return lo
		}
		return lo + rng.Int63n(span+1)
	}
}

// --- 小道具 ---------------------------------------------------------------

// ensureVar は基底名の Var を用意する (無ければ既定レンジで作る)。
func ensureVar(sp *Spec, base string) *Var {
	if v, ok := sp.Vars[base]; ok {
		return v
	}
	v := &Var{
		Name: base,
		Type: Int,
		// 下限 / 上限とも Known=false の既定値で用意する。制約から実際に読めた側だけ
		// applyLoHi 等が Known=true の Bound で上書きする。どちらかが未確定なら
		// ParseSpec が警告 + coverage=partial を立てる。
		Min: Bound{Const: defaultIntMin},
		Max: Bound{Const: defaultIntMax},
	}
	sp.Vars[base] = v
	return v
}

func nonEmptyLines(s string) []string {
	var out []string
	for _, l := range strings.Split(s, "\n") {
		l = strings.TrimRight(l, " \t\r")
		if strings.TrimSpace(l) == "" {
			continue
		}
		out = append(out, l)
	}
	return out
}

func fields(line string) []string { return strings.Fields(line) }

// isContinuation は縦反復の継続マーカー行か。
func isContinuation(line string) bool {
	t := strings.TrimSpace(line)
	switch t {
	case ":", "：", "⋮", "︙", "...", "…", "\\vdots", "$\\vdots$", "\\vdots$", "$\\vdots":
		return true
	}
	return false
}

// subscriptBase は "A_1" / "A_i" / "A" の基底名 "A" を返す。数値だけ / 記号は "".
func subscriptBase(tok string) string {
	if i := strings.IndexByte(tok, '_'); i >= 0 {
		tok = tok[:i]
	}
	tok = strings.TrimSpace(tok)
	if tok == "" || !isIdentStart(tok[0]) {
		return ""
	}
	return tok
}

// subscriptOf は "A_N" の添字 "N" を返す。添字が無ければ "".
func subscriptOf(tok string) string {
	i := strings.IndexByte(tok, '_')
	if i < 0 {
		return ""
	}
	sub := tok[i+1:]
	sub = strings.Trim(sub, "{}")
	// "N,1" のような多重添字は先頭を採る。
	if j := strings.IndexByte(sub, ','); j >= 0 {
		sub = sub[:j]
	}
	return strings.TrimSpace(sub)
}

// allSubscript は toks が全て添字 want (例 "1") を持つか。
func allSubscript(toks []string, want string) bool {
	for _, t := range toks {
		if subscriptOf(t) != want {
			return false
		}
	}
	return len(toks) > 0
}

// baseTokens は toks の基底名スライスを返す (空は除く)。
func baseTokens(toks []string) []string {
	var out []string
	for _, t := range toks {
		if b := subscriptBase(t); b != "" {
			out = append(out, b)
		}
	}
	return out
}

// boundFromSubscript は添字 (N / N-1 / 5) を配列長 / 反復回数の Bound にする。
func boundFromSubscript(sub string) Bound {
	if b, ok := parseBound(sub); ok {
		return b
	}
	return constBound(1)
}

func isNumeric(s string) bool {
	_, ok := evalNumber(strings.ReplaceAll(s, " ", ""))
	return ok
}

func sortedVarNames(m map[string]*Var) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	// 安定した順序 (辞書順) で警告を出す。
	for i := 0; i < len(out); i++ {
		for j := i + 1; j < len(out); j++ {
			if out[j] < out[i] {
				out[i], out[j] = out[j], out[i]
			}
		}
	}
	return out
}
