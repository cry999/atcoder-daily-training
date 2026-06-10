package ui

// NavKind はナビゲーションの種別 (要件 027)。
type NavKind int

const (
	NavLetterNext  NavKind = iota // :next / :n  — 問題記号 (letter) +1
	NavLetterPrev                 // :prev / :p  — 問題記号 (letter) -1
	NavContestNext                // :fwd  / :f  — コンテスト番号 +1 (letter 保持)
	NavContestPrev                // :back / :b  — コンテスト番号 -1 (letter 保持)
	NavExplicit                   // :e <spec>   — 任意ジャンプ
)

// NavRequest は chat がパースしたナビゲーション要求。
// Spec は NavExplicit のときの :e 引数 (それ以外は空)。
type NavRequest struct {
	Kind NavKind
	Spec string
}

// NavMsg は chat が親 (startSplitModel) に渡す tea.Msg。
// ChatHeader.NavEnabled が真のときだけ発火する (start 分割画面限定)。
type NavMsg struct{ Req NavRequest }

// navRequestFor は command (parseCommand の結果) をナビゲーション要求に写像する純粋関数。
// ナビゲーションコマンドでなければ ok=false。chat はこれで NavMsg を組む。
func navRequestFor(cmd command) (NavRequest, bool) {
	switch cmd.name {
	case "next":
		return NavRequest{Kind: NavLetterNext}, true
	case "prev":
		return NavRequest{Kind: NavLetterPrev}, true
	case "fwd":
		return NavRequest{Kind: NavContestNext}, true
	case "back":
		return NavRequest{Kind: NavContestPrev}, true
	case "e":
		return NavRequest{Kind: NavExplicit, Spec: cmd.arg}, true
	default:
		return NavRequest{}, false
	}
}
