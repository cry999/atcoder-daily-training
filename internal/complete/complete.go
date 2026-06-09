// Package complete は atcoder CLI のシェル補完候補を生成する。
//
// 候補生成ロジックをここに集約し、各シェル (bash/zsh/fish) の補完スクリプトは
// 隠しヘルパ `atcoder __complete` を呼ぶだけの薄いラッパに保つ。Complete は
// 決して error を返さない (補完を壊さないため、I/O エラーは握りつぶす)。
package complete

import (
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/contestmeta"
	"github.com/cry999/atcoder-daily-training/internal/layout"
)

// contestPrefixes は contest_id を構成するレイアウト接頭辞。
var contestPrefixes = []string{"abc", "arc", "awc", "agc", "ahc"}

// layoutValues は --layout フラグが取りうる値。
var layoutValues = []string{"auto", "abc", "exercise"}

// shells は completion サブコマンドが対応するシェル。
var shells = []string{"bash", "zsh", "fish"}

// valueFlags は値を 1 つ取るフラグ (次トークンがその値になる)。位置引数の判定で
// 値トークンを読み飛ばすのに使う。
var valueFlags = map[string]bool{
	"--task": true, "--tasks": true, "--layout": true, "--timeout": true,
	"--case": true, "-c": true, "--in": true, "-i": true,
	"--out": true, "-o": true, "--jobs": true, "-j": true,
	"--tolerance": true,
}

// subFlags は各サブコマンドのフラグ候補。cmd/atcoder/*.go の実フラグと一致させる
// (フラグを足したらここも更新する)。
var subFlags = map[string][]string{
	"new":    {"--tasks", "--refresh", "--no-skeleton", "--no-fetch"},
	"test":   {"--task", "--refresh", "--timeout", "--case", "-c", "--layout", "--jobs", "-j", "--watch", "-w", "-v", "--verbose", "-d", "--debug", "-s", "--side-by-side", "--tolerance"},
	"run":    {"--task", "--in", "-i", "--out", "-o", "--interactive", "-I", "--timeout", "-v", "--verbose", "-d", "--debug", "--layout", "--tolerance"},
	"submit": {"--task", "--refresh", "--layout", "--no-open"},
	"stats":  {"--week", "--month", "--year"},
}

// takesContest はそのサブコマンドが <contest> 位置引数を取るか。
var takesContest = map[string]bool{"test": true, "run": true, "submit": true}

// Subcommands は補完対象のサブコマンド名を返す (__complete は隠すので含めない)。
func Subcommands() []string {
	return []string{"new", "test", "run", "submit", "stats", "commit", "completion"}
}

// Flags は指定サブコマンドのフラグ候補を返す。未知サブコマンドは nil。
func Flags(sub string) []string {
	return subFlags[sub]
}

// Contests は root 配下の abc/arc/awc ディレクトリと fetch 済みキャッシュから
// contest_id 候補を集める (和集合・重複排除・ソート)。I/O エラーは無視。
func Contests(root string) []string {
	set := map[string]struct{}{}
	for _, pfx := range contestPrefixes {
		entries, err := os.ReadDir(filepath.Join(root, pfx))
		if err != nil {
			continue
		}
		for _, e := range entries {
			if e.IsDir() {
				set[pfx+e.Name()] = struct{}{}
			}
		}
	}
	// キャッシュ dir (Base()/atcoder-tools/) 直下の contest_id。
	if entries, err := os.ReadDir(cachepath.Contest("")); err == nil {
		for _, e := range entries {
			if e.IsDir() {
				set[e.Name()] = struct{}{}
			}
		}
	}
	return sortedKeys(set)
}

// Tasks は contest の letter 候補を返す (既存解答ファイル + contest.toml の tasks)。
// 何も見つからなければ既定の a〜g を返す。
func Tasks(root, contest string) []string {
	set := map[string]struct{}{}
	if pfx, num, ok := splitContest(contest); ok {
		entries, err := os.ReadDir(filepath.Join(root, pfx, num))
		if err == nil {
			for _, e := range entries {
				if name := e.Name(); strings.HasSuffix(name, ".py") {
					set[strings.TrimSuffix(name, ".py")] = struct{}{}
				}
			}
		}
	}
	if m, err := contestmeta.Load(contestmeta.Path(contest)); err == nil {
		for _, t := range m.Tasks {
			if l, err := layout.Letter(t); err == nil {
				set[l] = struct{}{}
			}
		}
	}
	if len(set) == 0 {
		return []string{"a", "b", "c", "d", "e", "f", "g"}
	}
	return sortedKeys(set)
}

// Complete は `atcoder` 以降のトークン列 (末尾が補完中の単語) を受け取り、次単語の
// 候補を返す。__complete の本体。決して error を返さない。
func Complete(root string, words []string) []string {
	if len(words) == 0 {
		return Subcommands()
	}
	cur := words[len(words)-1]

	// サブコマンド位置。
	if len(words) == 1 {
		return filterPrefix(Subcommands(), cur)
	}
	sub := words[0]

	// 値を取るフラグの直後。
	if len(words) >= 2 {
		switch words[len(words)-2] {
		case "--task":
			if c := contestOf(sub, positionals(words)); c != "" {
				return filterPrefix(Tasks(root, c), cur)
			}
			return nil
		case "--layout":
			return filterPrefix(layoutValues, cur)
		}
	}

	// completion の shell 引数。
	if sub == "completion" {
		return filterPrefix(shells, cur)
	}

	// フラグ補完。
	if strings.HasPrefix(cur, "-") {
		return filterPrefix(Flags(sub), cur)
	}

	// 位置引数の補完。cur を除いた既出の位置引数で判定する。
	posBefore := positionals(words[:len(words)-1])
	switch {
	case sub == "new":
		if len(posBefore) == 0 {
			return filterPrefix([]string{"abc"}, cur) // モード名
		}
		if len(posBefore) == 1 && posBefore[0] == "abc" {
			return filterPrefix(Contests(root), cur)
		}
	case takesContest[sub]:
		if len(posBefore) == 0 {
			return filterPrefix(Contests(root), cur)
		}
	}
	return nil
}

// positionals は sub を除いたトークン列から位置引数だけを抜き出す。フラグ (- 始まり)
// と、値を取るフラグの直後のトークンは読み飛ばす。
func positionals(words []string) []string {
	var pos []string
	skip := false
	for _, w := range words[1:] { // words[0] = サブコマンド
		if skip {
			skip = false
			continue
		}
		if strings.HasPrefix(w, "-") {
			if valueFlags[w] {
				skip = true
			}
			continue
		}
		pos = append(pos, w)
	}
	return pos
}

// contestOf は位置引数列から確定済みの contest_id を取り出す。
func contestOf(sub string, pos []string) string {
	switch sub {
	case "new":
		if len(pos) >= 2 && pos[0] == "abc" {
			return pos[1]
		}
	case "test", "run", "submit":
		if len(pos) >= 1 {
			return pos[0]
		}
	}
	return ""
}

// splitContest は contest_id を接頭辞と番号に分ける (例 "abc457" → "abc","457")。
func splitContest(contest string) (pfx, num string, ok bool) {
	for _, p := range contestPrefixes {
		if strings.HasPrefix(contest, p) && len(contest) > len(p) {
			return p, contest[len(p):], true
		}
	}
	return "", "", false
}

func filterPrefix(cands []string, prefix string) []string {
	var out []string
	for _, c := range cands {
		if strings.HasPrefix(c, prefix) {
			out = append(out, c)
		}
	}
	return out
}

func sortedKeys(set map[string]struct{}) []string {
	out := make([]string, 0, len(set))
	for k := range set {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}
