// Package cliargs は、Go 標準 flag に渡す前に引数列を「フラグ + その値」と
// 「位置引数」に分離する薄い前処理を提供する。
//
// Go の flag は最初の非フラグ引数で解析を打ち切る (インターリーブ不可)。各
// サブコマンドが位置引数 (contest など) を先に手剥がししている都合と合わさり、
// 位置引数は先頭限定になっていた。Split を flag.Parse の前に噛ませることで、
// 位置引数とフラグを任意の順序で混在して打てるようにする。
//
// value-flag (次のトークンを値として取るフラグ) の集合はここに一本化し、
// internal/complete (補完の位置引数判定) もこれを共有する (single source of truth)。
package cliargs

import "strings"

// valueFlags は「次のトークンを値として取る」フラグ名 (先頭の "-"/"--" 込み) の集合。
// cmd/atcoder/*.go の flag 定義 (flags.String/Int/Float64/Duration 等) と一致させること。
// bool フラグ (--refresh, -s, --watch 等) は値を取らないので含めない。
var valueFlags = map[string]bool{
	"--task": true, "--tasks": true, "--layout": true, "--timeout": true,
	"--case": true, "-c": true, "--in": true, "-i": true,
	"--out": true, "-o": true, "--jobs": true, "-j": true,
	"--tolerance": true, "--last": true, "-l": true,
	"--time-limit": true,
}

// TakesValue は name (先頭の "-"/"--" 込み) が値を取るフラグかを返す。
func TakesValue(name string) bool { return valueFlags[name] }

// Split は引数列を「フラグ + その値」(flagArgs) と「位置引数」(positionals) に
// 分離する。順序は各列の中で保持する。flagArgs を flag.Parse へ、positionals を
// contest/category 等に使う。Split 自体はエラーを返さない (文字列分離のみ。誤りは
// 後段の flag.Parse / 位置引数チェックで顕在化する)。
//
// 規則:
//   - "--" 終端: 以降は全て positional。
//   - "-"/"--" 始まり (長さ 2 以上) はフラグ:
//   - "=" を含む (--task=d) → 値内包。次トークンは消費しない。
//   - value-flag → フラグ + 次トークン (値) を flagArgs へ。次を消費。
//   - それ以外 → bool フラグとして flagArgs へ。
//   - 上記以外 ("-" 単体を含む) は positional。
func Split(args []string) (flagArgs, positionals []string) {
	for i := 0; i < len(args); i++ {
		a := args[i]

		// "--" 終端: 残りは全て位置引数。
		if a == "--" {
			positionals = append(positionals, args[i+1:]...)
			break
		}

		// フラグ: "-" で始まり、長さ 2 以上 ("-" 単体は位置引数 = stdin marker 等)。
		if len(a) >= 2 && a[0] == '-' {
			flagArgs = append(flagArgs, a)
			// "--task=d" のように値内包なら次トークンは消費しない。
			if strings.Contains(a, "=") {
				continue
			}
			// value-flag は次トークンを値として連れる (あれば)。
			if valueFlags[a] && i+1 < len(args) {
				flagArgs = append(flagArgs, args[i+1])
				i++
			}
			continue
		}

		// 位置引数。
		positionals = append(positionals, a)
	}
	return flagArgs, positionals
}
