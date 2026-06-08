package ui

import (
	"fmt"
	"strings"
)

// 表示形式は delta / Claude Code の unified diff を模す:
//   - 既定は変化のあった行だけ (no-context)。full=true ならマッチ行も
//     " " (空白) サイン + dim 表示の context 行として出す。
//   - 左に line number + " │ " gutter
//   - 行全体に subtle な背景色 (赤 / 緑)、変化のあった token だけ強調背景
//   - LCS による行整列と、ペアになった行は token 単位の intra-line diff を行う

type diffKind int

const (
	diffKeep diffKind = iota
	diffDel
	diffAdd
)

type diffOp struct {
	Kind diffKind
	Text string
}

// lcsDiff は a, b に対する LCS ベースの編集列を返す。
// 競技プログラミングの出力サイズなら O(n*m) で十分。
func lcsDiff(a, b []string) []diffOp {
	n, m := len(a), len(b)
	dp := make([][]int, n+1)
	for i := range dp {
		dp[i] = make([]int, m+1)
	}
	for i := 0; i < n; i++ {
		for j := 0; j < m; j++ {
			if a[i] == b[j] {
				dp[i+1][j+1] = dp[i][j] + 1
			} else if dp[i+1][j] >= dp[i][j+1] {
				dp[i+1][j+1] = dp[i+1][j]
			} else {
				dp[i+1][j+1] = dp[i][j+1]
			}
		}
	}
	var ops []diffOp
	i, j := n, m
	for i > 0 || j > 0 {
		switch {
		case i > 0 && j > 0 && a[i-1] == b[j-1]:
			ops = append(ops, diffOp{Kind: diffKeep, Text: a[i-1]})
			i--
			j--
		case i == 0 || (j > 0 && dp[i][j-1] >= dp[i-1][j]):
			ops = append(ops, diffOp{Kind: diffAdd, Text: b[j-1]})
			j--
		default:
			ops = append(ops, diffOp{Kind: diffDel, Text: a[i-1]})
			i--
		}
	}
	for l, r := 0, len(ops)-1; l < r; l, r = l+1, r-1 {
		ops[l], ops[r] = ops[r], ops[l]
	}
	return ops
}

// renderDiff は expected と actual の unified diff 文字列を返す。
// 各行は "<indent><lineNo> │ <sign> <tokens...>\n" の形。
//   - full=false: 変化のあった行だけ (簡潔)
//   - full=true : マッチ行も " " サイン付きの context 行として出す (-v 用)
//
// LCS が返す op 列は「同じ hunk 内で del を全部出してから add を全部」とい
// う形になりがちなので、hunk (連続する非 keep 区間) をまず切り出し、その中
// で del を adds と 1:1 でペアにする。
func renderDiff(expected, actual string, full bool) string {
	expLines := strings.Split(expected, "\n")
	actLines := strings.Split(actual, "\n")
	ops := lcsDiff(expLines, actLines)

	var sb strings.Builder
	expN, actN := 0, 0
	i := 0
	for i < len(ops) {
		if ops[i].Kind == diffKeep {
			expN++
			actN++
			if full {
				sb.WriteString(renderContextLine(ops[i].Text, expN))
			}
			i++
			continue
		}
		// hunk: 連続する非 keep
		start := i
		for i < len(ops) && ops[i].Kind != diffKeep {
			i++
		}
		var dels, adds []string
		for k := start; k < i; k++ {
			if ops[k].Kind == diffDel {
				dels = append(dels, ops[k].Text)
			} else {
				adds = append(adds, ops[k].Text)
			}
		}
		pairs := len(dels)
		if len(adds) < pairs {
			pairs = len(adds)
		}
		for k := 0; k < pairs; k++ {
			expN++
			actN++
			sb.WriteString(renderDiffPair(dels[k], adds[k], expN, actN))
		}
		for k := pairs; k < len(dels); k++ {
			expN++
			sb.WriteString(renderSoloLine(dels[k], expN, true))
		}
		for k := pairs; k < len(adds); k++ {
			actN++
			sb.WriteString(renderSoloLine(adds[k], actN, false))
		}
	}
	return sb.String()
}

// renderContextLine は match した行を unified diff 風に " " (空白) サイン付きで描画する。
// 背景色は付けず、本文も dim foreground にして「変化点ではない」ことを視覚的に示す。
func renderContextLine(line string, n int) string {
	var sb strings.Builder
	sb.WriteString("         ")
	sb.WriteString(diffLineNumStyle.Render(fmt.Sprintf("%3d", n)))
	sb.WriteString(diffGutterStyle.Render(" │ "))
	sb.WriteString("  ") // "- " / "+ " と桁を揃える
	sb.WriteString(diffContextStyle.Render(line))
	sb.WriteString("\n")
	return sb.String()
}

func renderDiffPair(expLine, actLine string, expN, actN int) string {
	expToks := strings.Fields(expLine)
	actToks := strings.Fields(actLine)
	tokOps := lcsDiff(expToks, actToks)
	return renderTokenLine(tokOps, expN, true) + renderTokenLine(tokOps, actN, false)
}

// renderSoloLine はペアの相手がいない (片側にしかない) 行を出力する。
// 全 token を変化 (emph) として描画。
func renderSoloLine(line string, n int, minus bool) string {
	toks := strings.Fields(line)
	ops := make([]diffOp, len(toks))
	kind := diffAdd
	if minus {
		kind = diffDel
	}
	for i, t := range toks {
		ops[i] = diffOp{Kind: kind, Text: t}
	}
	return renderTokenLine(ops, n, minus)
}

// renderTokenLine は token ops から 1 本の diff 行 (改行込み) を生成する。
// minus=true なら "-" 側の行 (add op は無視)、false なら "+" 側 (del op は無視)。
func renderTokenLine(ops []diffOp, n int, minus bool) string {
	lineStyle := diffPlusLineStyle
	emphStyle := diffPlusEmphStyle
	signStyle := diffPlusSignStyle
	if minus {
		lineStyle = diffMinusLineStyle
		emphStyle = diffMinusEmphStyle
		signStyle = diffMinusSignStyle
	}

	var sb strings.Builder
	sb.WriteString("         ")
	sb.WriteString(diffLineNumStyle.Render(fmt.Sprintf("%3d", n)))
	sb.WriteString(diffGutterStyle.Render(" │ "))
	if minus {
		sb.WriteString(signStyle.Render("- "))
	} else {
		sb.WriteString(signStyle.Render("+ "))
	}

	first := true
	for _, op := range ops {
		// 自分側でない op はスキップ
		if minus && op.Kind == diffAdd {
			continue
		}
		if !minus && op.Kind == diffDel {
			continue
		}
		if !first {
			sb.WriteString(lineStyle.Render(" "))
		}
		first = false
		if op.Kind == diffKeep {
			sb.WriteString(lineStyle.Render(op.Text))
		} else {
			sb.WriteString(emphStyle.Render(op.Text))
		}
	}
	sb.WriteString("\n")
	return sb.String()
}
