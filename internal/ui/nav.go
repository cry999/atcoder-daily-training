package ui

import "strings"

// NavKind はナビゲーションの種別 (要件 027)。
type NavKind int

const (
	NavLetterNext      NavKind = iota // :task next / :task n      — 問題記号 (letter) +1
	NavLetterPrev                     // :task prev / :task p      — 問題記号 (letter) -1
	NavContestNext                    // :contest next / :contest n — コンテスト番号 +1 (letter 保持)
	NavContestPrev                    // :contest prev / :contest p — コンテスト番号 -1 (letter 保持)
	NavExplicit                       // :e <spec>                  — 任意ジャンプ
	NavLetterExplicit                 // :task <letter>             — 記号を直指定 (現コンテスト)。Spec=letter
	NavContestExplicit                // :contest <num|id>          — コンテストを直指定 (letter 保持)。Spec=指定
)

// NavRequest は chat がパースしたナビゲーション要求。
// Spec は直指定系 (NavExplicit / NavLetterExplicit / NavContestExplicit) の引数 (相対移動では空)。
type NavRequest struct {
	Kind NavKind
	Spec string
}

// NavMsg は chat が親 (startSplitModel) に渡す tea.Msg。
// ChatHeader.NavEnabled が真のときだけ発火する (start 分割画面限定)。
type NavMsg struct{ Req NavRequest }

// navRequestFor は command (parseCommand の結果) をナビゲーション要求に写像する純粋関数。
// :task / :contest は第 2 トークン (next|n / prev|p) で方向が決まる。ナビゲーション
// コマンドでない・第 2 トークンが欠落/不正なら ok=false。chat はこれで NavMsg を組む。
func navRequestFor(cmd command) (NavRequest, bool) {
	switch cmd.name {
	case "task":
		switch navSub(cmd.arg) {
		case "next":
			return NavRequest{Kind: NavLetterNext}, true
		case "prev":
			return NavRequest{Kind: NavLetterPrev}, true
		}
		// next/prev 以外の非空トークンは記号の直指定 (:task f)。
		if tok := navFirstToken(cmd.arg); tok != "" {
			return NavRequest{Kind: NavLetterExplicit, Spec: tok}, true
		}
		return NavRequest{}, false
	case "contest":
		switch navSub(cmd.arg) {
		case "next":
			return NavRequest{Kind: NavContestNext}, true
		case "prev":
			return NavRequest{Kind: NavContestPrev}, true
		}
		// next/prev 以外の非空トークンはコンテストの直指定 (:contest 123 / :contest arc100)。
		if tok := navFirstToken(cmd.arg); tok != "" {
			return NavRequest{Kind: NavContestExplicit, Spec: tok}, true
		}
		return NavRequest{}, false
	case "e":
		return NavRequest{Kind: NavExplicit, Spec: cmd.arg}, true
	default:
		return NavRequest{}, false
	}
}

// navSub は :task / :contest の第 2 トークンを向き ("next" / "prev") に正規化する。
// next|n → "next"、prev|p → "prev"。欠落・不正なら "" (呼び出し側が利用法を案内)。
func navSub(arg string) string {
	f := strings.Fields(arg)
	if len(f) == 0 {
		return ""
	}
	switch strings.ToLower(f[0]) {
	case "next", "n":
		return "next"
	case "prev", "p":
		return "prev"
	default:
		return ""
	}
}

// navFirstToken は arg の第 1 トークンを返す (直指定の Spec)。空白のみ・空なら ""。
func navFirstToken(arg string) string {
	f := strings.Fields(arg)
	if len(f) == 0 {
		return ""
	}
	return f[0]
}
