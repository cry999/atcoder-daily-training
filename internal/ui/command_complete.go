package ui

import (
	"sort"
	"strings"
)

// 補完候補の単一情報源 (要件 031)。canonical 名のみを返し、別名 (c/n/p 等) は
// 候補に出さない (入力中のプレフィックスとしては parseCommand が受理する)。
var (
	// 常時出すコマンド名 (`:debug`/`:cheat` は要件 030、`:replay` は要件 039、`:test` は要件 045、
	// `:meta` は要件 055、`:gen` は要件 060 で追加)。
	completeNamesBase = []string{"case", "cheat", "debug", "gen", "meta", "q", "replay", "set", "test", "w"}
	// NavEnabled (start 分割画面) のときだけ出すコマンド名 (要件 027)。
	completeNamesNav = []string{"contest", "e", "task"}
	// 第 2 トークンの候補 (1 語目 → サブトークン)。:set は verify/noverify に加え
	// Debug 表示トグルの debug/nodebug も取る (要件 030)。:meta は fetch/url/time_limit
	// (要件 055 / 057)。
	completeSubTokens = map[string][]string{
		"set":     {"debug", "nodebug", "noverify", "verify"},
		"task":    {"next", "prev"},
		"contest": {"next", "prev"},
		"meta":    {"fetch", "time_limit", "url"},
	}
	// 後続トークンを取るコマンド (一意確定時に末尾へ空白を足す)。
	completeExpectsArg = map[string]bool{"set": true, "task": true, "contest": true, "e": true, "test": true, "meta": true}
)

// commandNames は補完で出すコマンド名一覧をアルファベット順で返す。
// navEnabled が真なら task/contest/e (start 限定) を含める。
func commandNames(navEnabled bool) []string {
	names := append([]string(nil), completeNamesBase...)
	if navEnabled {
		names = append(names, completeNamesNav...)
	}
	sort.Strings(names)
	return names
}

// completeCommandLine は command モードの `:` 行 line を Tab 補完する純粋関数 (要件 031)。
// navEnabled は task/contest/e を候補に含めるか。replacement は補完後の行 (変化が無ければ
// line と同じ)、candidates は複数一致のとき表示する候補一覧 (1 件確定・0 件なら nil)。
func completeCommandLine(line string, navEnabled bool) (replacement string, candidates []string) {
	fields := strings.Fields(line)
	endsWithSpace := line != "" && (line[len(line)-1] == ' ' || line[len(line)-1] == '\t')

	switch {
	// 第 1 トークン (コマンド名): 空、または 1 語目を入力中。
	case len(fields) == 0 || (len(fields) == 1 && !endsWithSpace):
		cur := ""
		if len(fields) == 1 {
			cur = fields[0]
		}
		matches := filterByPrefix(commandNames(navEnabled), cur)
		return applyCompletion("", cur, matches)

	// 第 2 トークン (サブトークン): 1 語目 + 空白、または 2 語目を入力中。
	case (len(fields) == 1 && endsWithSpace) || (len(fields) == 2 && !endsWithSpace):
		subs := completeSubTokens[fields[0]]
		if len(subs) == 0 {
			return line, nil
		}
		cur := ""
		if len(fields) == 2 {
			cur = fields[1]
		}
		matches := filterByPrefix(subs, cur)
		return applyCompletion(fields[0]+" ", cur, matches)

	// 第 3 トークン以降は補完しない。
	default:
		return line, nil
	}
}

// applyCompletion は前方一致した matches から補完結果を組む。
//   - 0 件: 行は変えない (prefix+cur をそのまま返す)。
//   - 1 件: その候補で確定。後続トークンを取るコマンドなら末尾に空白を足す。
//   - 複数: 最長共通プレフィックスまで伸ばし、候補一覧を返す。
func applyCompletion(prefix, cur string, matches []string) (string, []string) {
	switch len(matches) {
	case 0:
		return prefix + cur, nil
	case 1:
		repl := prefix + matches[0]
		if completeExpectsArg[matches[0]] {
			repl += " "
		}
		return repl, nil
	default:
		return prefix + longestCommonPrefix(matches), matches
	}
}

// filterByPrefix は cands のうち prefix に前方一致するものを順序を保って返す。
func filterByPrefix(cands []string, prefix string) []string {
	var out []string
	for _, c := range cands {
		if strings.HasPrefix(c, prefix) {
			out = append(out, c)
		}
	}
	return out
}

// longestCommonPrefix は文字列群の最長共通プレフィックスを返す。
func longestCommonPrefix(ss []string) string {
	if len(ss) == 0 {
		return ""
	}
	p := ss[0]
	for _, s := range ss[1:] {
		for !strings.HasPrefix(s, p) {
			p = p[:len(p)-1]
			if p == "" {
				return ""
			}
		}
	}
	return p
}
