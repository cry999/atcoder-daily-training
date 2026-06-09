// Package alias は atcoder のコマンド alias を展開する。
//
// config.toml の [alias] (名前→コマンド列) を使い、先頭トークンが alias なら
// そのコマンド列に展開し、残りの引数を後ろに連結する。組み込みサブコマンドは
// 常に優先して展開しない (alias は未知名のときだけ解決される)。alias → alias を
// 再帰展開し、同じ alias を二度たどったらループとして error を返す。
//
// 値の分割は空白区切り (strings.Fields)。クォートを含む 1 引数は将来対応。
//
// 要件詳細: docs/tools/requirements/016-config-alias.md
package alias

import (
	"fmt"
	"strings"
)

// Expand は args の先頭が alias なら展開し、残りの引数を後ろに連結して返す。
// isBuiltin が true を返す先頭トークンは展開しない (組み込み優先)。alias でも
// 組み込みでもない先頭はそのまま返す (呼び出し側が未知として usage を出す)。
//
//	args=["upd-lo","--check"], aliases={"upd-lo":"update --local"}
//	  → ["update","--local","--check"]
func Expand(args []string, aliases map[string]string, isBuiltin func(string) bool) ([]string, error) {
	if len(args) == 0 {
		return args, nil
	}
	seen := map[string]bool{}
	for {
		head := args[0]
		if isBuiltin(head) {
			return args, nil // 組み込みは常に優先
		}
		expansion, ok := aliases[head]
		if !ok {
			return args, nil // alias でも組み込みでもない → そのまま返す
		}
		if seen[head] {
			return nil, fmt.Errorf("alias loop detected: %s", head)
		}
		seen[head] = true

		tokens := strings.Fields(expansion)
		if len(tokens) == 0 {
			return nil, fmt.Errorf("alias %q is empty", head)
		}
		// tokens + 元の追加引数 (args[1:]) を連結。
		next := make([]string, 0, len(tokens)+len(args)-1)
		next = append(next, tokens...)
		next = append(next, args[1:]...)
		args = next
	}
}
