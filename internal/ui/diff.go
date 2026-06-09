package ui

import (
	"fmt"
	"os"
	"strings"

	"github.com/charmbracelet/lipgloss"
	"golang.org/x/term"
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
// レイアウト: "<3d 行番号> <空サイン> │ <本文>" (sign は - / + の桁を埋める空白)。
func renderContextLine(line string, n int) string {
	var sb strings.Builder
	sb.WriteString("         ")
	sb.WriteString(diffLineNumStyle.Render(fmt.Sprintf("%3d", n)))
	sb.WriteString(" ") // line number と sign の間
	sb.WriteString(" ") // sign の位置 (context は空)
	sb.WriteString(diffGutterStyle.Render(" │ "))
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
	lineNumStyle := diffPlusLineNumStyle
	if minus {
		lineStyle = diffMinusLineStyle
		emphStyle = diffMinusEmphStyle
		signStyle = diffMinusSignStyle
		lineNumStyle = diffMinusLineNumStyle
	}

	var sb strings.Builder
	// レイアウト: "<3d 行番号> <sign> │ <内容>" — sign を gutter の右ではなく
	// 行番号の隣に置くことで、左半 ("行を識別する情報") と右半 ("実際の出力") を
	// 視覚的に分離する。行番号自体も "-"/"+" の色 (red/green) に着色して
	// どちら側の行か一目で判別できるようにする。
	sb.WriteString("         ")
	sb.WriteString(lineNumStyle.Render(fmt.Sprintf("%3d", n)))
	sb.WriteString(" ")
	if minus {
		sb.WriteString(signStyle.Render("-"))
	} else {
		sb.WriteString(signStyle.Render("+"))
	}
	sb.WriteString(diffGutterStyle.Render(" │ "))

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

// ---- side-by-side diff ----
//
// レイアウト (1 行):
//
//	<indent><左 content padded> │ <expN> │-+│ <actN> │ <右 content>
//
// 期待値ライン (左) と実際のライン (右) を直接並べ、中央には両方の行番号
// を "│" で囲って出す。行番号自体は前景を dim neutral に保ち、minus/plus
// の識別は背景色 (薄い赤 / 緑) で示す。中央 sigil "│-+│" は行番号囲いの
// "│" を共有する形になっており、左の "-" は期待値側 (minus) の sign、右の
// "+" は実際値側 (plus) の sign。active な sign だけ色付きで出す:
//
//	paired :  │ N │-+│ N │   (-=red / +=green)
//	solo - :  │ N │- │   │
//	solo + :  │   │ +│ N │
//	context:  │ N │  │ N │

type sbRowKind int

const (
	sbRowPaired sbRowKind = iota
	sbRowSoloDel
	sbRowSoloAdd
	sbRowContext
)

const (
	diffSBIndent = "  "
	// 中央ブロックの幅: " │ <3d> │<2-char sigil>│ <3d> │ "
	//   = 1+1+1+3+1+1+2+1+1+3+1+1+1 = 18
	diffSBCenterWidth = 18
)

// renderDiffSideBySide は expected を左、actual を右、中央に両方の行番号 +
// sigil を出す形式で diff を返す。full=true ならマッチ行も両側に出す。
func renderDiffSideBySide(expected, actual string, full bool) string {
	totalW := terminalWidth()
	half := (totalW - len(diffSBIndent) - diffSBCenterWidth) / 2
	if half < 16 {
		half = 16
	}

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
				left := renderSBContextSide(ops[i].Text, half)
				right := renderSBContextSide(ops[i].Text, half)
				sb.WriteString(diffSBIndent + left + renderSBCenter(expN, actN, sbRowContext) + right + "\n")
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
			expToks := strings.Fields(dels[k])
			actToks := strings.Fields(adds[k])
			tokOps := lcsDiff(expToks, actToks)
			left := renderSBPairSide(tokOps, true, half)
			right := renderSBPairSide(tokOps, false, half)
			sb.WriteString(diffSBIndent + left + renderSBCenter(expN, actN, sbRowPaired) + right + "\n")
		}
		for k := pairs; k < len(dels); k++ {
			expN++
			left := renderSBSoloSide(dels[k], true, half)
			right := strings.Repeat(" ", half)
			sb.WriteString(diffSBIndent + left + renderSBCenter(expN, 0, sbRowSoloDel) + right + "\n")
		}
		for k := pairs; k < len(adds); k++ {
			actN++
			left := strings.Repeat(" ", half)
			right := renderSBSoloSide(adds[k], false, half)
			sb.WriteString(diffSBIndent + left + renderSBCenter(0, actN, sbRowSoloAdd) + right + "\n")
		}
	}
	return sb.String()
}

// renderSBCenter は中央ブロック " │ <expN> │<-><+> │ <actN> │ " (18 桁) を返す。
// 行番号は "│" で囲われ、kind に応じて行番号の背景色 (minus/plus bg) と
// sigil の +/- の active 状態を決める。前景色は dim neutral で統一。
// 左半 (" │ <es> │") は paired/soloDel で minus の薄い行 bg、右半
// ("│ <as> │ ") は paired/soloAdd で plus の薄い行 bg を持つ。中央 sigil の
// "-+" 2 文字は bg を持たず、左右 bg の継ぎ目になる。左の "-" は左側
// (expected) の sign、右の "+" は右側 (actual) の sign。
//
// 実装上の注意: lipgloss の nested Render は内側 reset ("\033[0m") の後に
// 外側 bg を再適用しないため、`diffMinusLineStyle.Render(" │ <es> │")` と
// 一括ラップすると bar や padding の bg が抜けて見える (左右で揃わない)。
// よって各セグメント (bar / padding / 行番号) を個別に bg 付きスタイルで
// 描画してから連結する。
func renderSBCenter(expN, actN int, kind sbRowKind) string {
	// 行番号スタイル: 前景は dim、背景で minus/plus を識別
	expStyle := diffLineNumStyle
	actStyle := diffLineNumStyle
	switch kind {
	case sbRowPaired:
		expStyle = diffMinusLineNumStyle
		actStyle = diffPlusLineNumStyle
	case sbRowSoloDel:
		expStyle = diffMinusLineNumStyle
	case sbRowSoloAdd:
		actStyle = diffPlusLineNumStyle
	}

	es := "   "
	as := "   "
	if expN > 0 {
		es = expStyle.Render(fmt.Sprintf("%3d", expN))
	}
	if actN > 0 {
		as = actStyle.Render(fmt.Sprintf("%3d", actN))
	}

	// sigil "│<plus><minus>│" — active な sign だけ色付き、それ以外は空白。
	// "+"/"-" 自体は bg を持たないので、左右 bg の中間の "通路" として機能する。
	plusCh := " "
	minusCh := " "
	switch kind {
	case sbRowPaired:
		plusCh = diffPlusSignFgStyle.Render("+")
		minusCh = diffMinusSignFgStyle.Render("-")
	case sbRowSoloAdd:
		plusCh = diffPlusSignFgStyle.Render("+")
	case sbRowSoloDel:
		minusCh = diffMinusSignFgStyle.Render("-")
	}

	// 左 chunk: " │ <es> │" の各セグメントを kind に応じて bg 付きで作る。
	leftSpace := " "
	leftBar := diffGutterStyle.Render("│")
	if kind == sbRowPaired || kind == sbRowSoloDel {
		leftSpace = diffMinusLineStyle.Render(" ")
		leftBar = diffMinusGutterStyle.Render("│")
	}
	leftChunk := leftSpace + leftBar + leftSpace + es + leftSpace + leftBar

	// 右 chunk: "│ <as> │ " の各セグメントを kind に応じて bg 付きで作る。
	rightSpace := " "
	rightBar := diffGutterStyle.Render("│")
	if kind == sbRowPaired || kind == sbRowSoloAdd {
		rightSpace = diffPlusLineStyle.Render(" ")
		rightBar = diffPlusGutterStyle.Render("│")
	}
	rightChunk := rightBar + rightSpace + as + rightSpace + rightBar + rightSpace

	// 左に "-" (期待値側 = minus)、右に "+" (実際値側 = plus)。
	return leftChunk + minusCh + plusCh + rightChunk
}

// renderSBContextSide は match 行の半側を返す (dim 本文を width に pad)。
// context は変化なしなので行 bg は付けない。
func renderSBContextSide(line string, width int) string {
	return padToWidth(diffContextStyle.Render(line), width)
}

// renderSBPairSide は paired diff の半側を返す。SBS でも行全体に薄い行 bg
// (diffMinusBg / diffPlusBg) を当てて minus/plus を識別する。intra-line emph
// は行 bg を保ったまま fg のみ red/green に上書きする (diffMinusEmphStyle /
// diffPlusEmphStyle)。
func renderSBPairSide(ops []diffOp, minus bool, width int) string {
	lineStyle := diffPlusLineStyle
	emphStyle := diffPlusEmphStyle
	if minus {
		lineStyle = diffMinusLineStyle
		emphStyle = diffMinusEmphStyle
	}
	var sb strings.Builder
	first := true
	for _, op := range ops {
		if minus && op.Kind == diffAdd {
			continue
		}
		if !minus && op.Kind == diffDel {
			continue
		}
		if !first {
			sb.WriteString(" ")
		}
		first = false
		if op.Kind == diffKeep {
			sb.WriteString(op.Text)
		} else {
			sb.WriteString(emphStyle.Render(op.Text))
		}
	}
	// Width(width) で bg 込みで右まで pad
	return lineStyle.Width(width).Render(sb.String())
}

// renderSBSoloSide はペア相手がいない 1 行の半側を返す (全 token を強調)。
func renderSBSoloSide(line string, minus bool, width int) string {
	toks := strings.Fields(line)
	ops := make([]diffOp, len(toks))
	kind := diffAdd
	if minus {
		kind = diffDel
	}
	for i, t := range toks {
		ops[i] = diffOp{Kind: kind, Text: t}
	}
	return renderSBPairSide(ops, minus, width)
}

// padToWidth は ANSI を含む文字列の可視幅を測って、指定幅まで空白でパディングする。
func padToWidth(s string, width int) string {
	visW := lipgloss.Width(s)
	if visW >= width {
		return s
	}
	return s + strings.Repeat(" ", width-visW)
}

// terminalWidth は os.Stdout の端末幅を返す。取得失敗時は 120 にフォールバック。
func terminalWidth() int {
	w, _, err := term.GetSize(int(os.Stdout.Fd()))
	if err != nil || w <= 0 {
		return 120
	}
	return w
}
