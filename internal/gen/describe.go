package gen

import (
	"fmt"
	"strings"
)

// Describe は --show-spec 用に、認識した入力形式・変数・警告・カバレッジを
// 人間可読な複数行文字列で返す。
func (s *Spec) Describe() string {
	var b strings.Builder
	b.WriteString("recognized input format:\n")
	for _, blk := range s.Blocks {
		b.WriteString("  " + describeBlock(blk) + "\n")
	}
	b.WriteString("variables:\n")
	for _, name := range sortedVarNames(s.Vars) {
		v := s.Vars[name]
		b.WriteString("  " + describeVar(v) + "\n")
	}
	b.WriteString("warnings:\n")
	if len(s.Warnings) == 0 {
		b.WriteString("  (none)\n")
	} else {
		for _, w := range s.Warnings {
			b.WriteString("  - " + w + "\n")
		}
	}
	b.WriteString("coverage: " + s.Coverage.String() + "\n")
	return b.String()
}

func describeBlock(blk Block) string {
	switch blk.Kind {
	case Scalar:
		return fmt.Sprintf("scalar : %s", strings.Join(blk.Tokens, " "))
	case Seq:
		layout := "row"
		if blk.Layout == Col {
			layout = "col"
		}
		return fmt.Sprintf("seq    : %s_1..%s_%s  (%s, len=%s)",
			blk.Var, blk.Var, describeBound(blk.Count), layout, describeBound(blk.Count))
	case Repeat:
		return fmt.Sprintf("repeat : %s   (count=%s)", strings.Join(subscripted(blk.Tokens), " "), describeBound(blk.Count))
	case Str:
		return fmt.Sprintf("string : %s", blk.Var)
	default:
		return "?"
	}
}

func subscripted(tokens []string) []string {
	out := make([]string, len(tokens))
	for i, t := range tokens {
		out[i] = t + "_i"
	}
	return out
}

func describeVar(v *Var) string {
	typ := "int"
	if v.Type == String {
		typ = "str"
	}
	lo, hi := describeBound(v.Min), describeBound(v.Max)
	if v.Type == String {
		return fmt.Sprintf("%-4s %-4s len %s .. %s  charset=%s", v.Name, typ, lo, hi, v.Charset)
	}
	return fmt.Sprintf("%-4s %-4s %s .. %s", v.Name, typ, lo, hi)
}

func describeBound(b Bound) string {
	if b.Ref != "" {
		if b.Offset > 0 {
			return fmt.Sprintf("%s+%d", b.Ref, b.Offset)
		}
		if b.Offset < 0 {
			return fmt.Sprintf("%s%d", b.Ref, b.Offset)
		}
		return b.Ref
	}
	return fmt.Sprintf("%d", b.Const)
}
