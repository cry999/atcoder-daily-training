// Package debugstrip は提出準備時に Python 解答ソースから [DEBUG] 出力 print を
// コメントアウトする。判定・実行には関与せず、文字列変換のみを行う純粋パッケージ。
//
// 既存の DEBUG 規約 (stdout 先頭が [DEBUG] の行をデバッグ出力とみなす。-d/--debug の
// splitDebug) をソース行の print に流用し、提出コードからデバッグ出力を取り除く。
package debugstrip

import (
	"regexp"
	"strings"
)

// debugPrintRe は行頭 (インデント可) が print(...) で、最初の引数が [DEBUG] で始まる
// 文字列リテラル (f/r 等のプレフィックス・"/' 可) の行にマッチする。
// 既にコメントアウト済み (行頭 #) の行は print 始まりにならないのでマッチしない (冪等)。
var debugPrintRe = regexp.MustCompile(`^[ \t]*print\s*\(\s*[A-Za-z]*["']\[DEBUG\]`)

// CommentOut は src 中の「行頭 (インデント可) が print(...) で最初の文字列引数が
// [DEBUG] で始まる」行をコメントアウトし、加工後ソースとコメントアウト件数を返す。
//
// コメントアウトするとブロックが空になり IndentationError を招く場合 (= 直前の非空行が
// ':' で終わる print で、そのブロックが [DEBUG] print・コメント・空行だけで構成される)
// は、そのブロック内の [DEBUG] print をまとめてスキップする。`if os.environ.get("DEBUG"):`
// ガード下の print はジャッジで DEBUG 未設定により実行されないので、残しても無害。
// 一方、ループや条件分岐に実コードと混在する [DEBUG] print はコメントアウトする。
//
// コメントアウト済み行は再マッチしないので冪等。失敗経路は持たない。
func CommentOut(src string) (string, int) {
	lines := strings.Split(src, "\n")
	prevNonBlank := ""
	// skipBlockIndent >= 0 のあいだ、その indent 以上の [DEBUG] print は
	// 「空ブロック化を避けるべき DEBUG-only ブロック」の一部としてスキップする。
	skipBlockIndent := -1
	n := 0
	for i := range lines {
		line := lines[i]
		stripped := strings.TrimLeft(line, " \t")
		blank := strings.TrimSpace(line) == ""
		ind := len(line) - len(stripped)

		// DEBUG-only ブロックの終端: インデントが閾値未満の非空行で抜ける。
		if skipBlockIndent >= 0 && !blank && ind < skipBlockIndent {
			skipBlockIndent = -1
		}

		if debugPrintRe.MatchString(line) {
			switch {
			case skipBlockIndent >= 0 && ind >= skipBlockIndent:
				// DEBUG-only ブロック内 → スキップ。
			case strings.HasSuffix(strings.TrimRight(prevNonBlank, " \t"), ":"):
				// ブロック先頭の print。ブロックが除去可能な行だけなら空ブロック化するので
				// ブロックごとスキップ。実コードが混在するならコメントアウトする。
				if blockAllRemovable(lines, i, ind) {
					skipBlockIndent = ind
				} else {
					lines[i] = line[:ind] + "# " + stripped
					n++
				}
			default:
				lines[i] = line[:ind] + "# " + stripped
				n++
			}
		}

		if strings.TrimSpace(lines[i]) != "" {
			prevNonBlank = lines[i]
		}
	}
	return strings.Join(lines, "\n"), n
}

// blockAllRemovable は start から始まるブロック (インデント >= blockIndent の範囲) が
// 除去可能な行 ([DEBUG] print・コメント・空行) だけで構成されるかを返す。実コードが
// 1 行でもあれば false (= コメントアウトしても空ブロックにならない)。
func blockAllRemovable(lines []string, start, blockIndent int) bool {
	for j := start; j < len(lines); j++ {
		if strings.TrimSpace(lines[j]) == "" {
			continue
		}
		ind := len(lines[j]) - len(strings.TrimLeft(lines[j], " \t"))
		if ind < blockIndent {
			break // ブロック終端 (dedent)。
		}
		if !removable(lines[j]) {
			return false
		}
	}
	return true
}

// removable はコメントアウトしても (またはコメントとして) ブロックに実体を残さない行か。
func removable(line string) bool {
	stripped := strings.TrimLeft(line, " \t")
	return strings.HasPrefix(stripped, "#") || debugPrintRe.MatchString(line)
}
