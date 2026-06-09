// Package complete は atcoder CLI のシェル補完候補を生成する。
//
// 候補生成ロジックをここに集約し、各シェル (bash/zsh/fish) の補完スクリプトは
// 隠しヘルパ `atcoder __complete` を呼ぶだけの薄いラッパに保つ。Complete は
// 決して error を返さない (補完を壊さないため、I/O エラーは握りつぶす)。
//
// 各候補は値 (Value) に加えて任意の説明 (Desc) を持つ。説明は zsh (_describe) と
// fish (tab 区切り) でユーザに見せる。bash は値のみを使う。
// 要件詳細: docs/tools/requirements/008-atcoder-completion.md,
// docs/tools/requirements/012-completion-descriptions.md。
package complete

import (
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/contestmeta"
	"github.com/cry999/atcoder-daily-training/internal/layout"
)

// Candidate は補完候補 1 件。Desc は空可 (説明なし)。
type Candidate struct {
	Value string
	Desc  string
}

// contestPrefixes は contest_id を構成するレイアウト接頭辞。
var contestPrefixes = []string{"abc", "arc", "awc", "agc", "ahc"}

// layoutCands は --layout フラグが取りうる値 (説明付き)。
var layoutCands = []Candidate{
	{"auto", "pick abc for abc<NNN>, else exercise"},
	{"abc", "abc/<contest>/<letter>.py layout"},
	{"exercise", "exercise/YYYY/MM/DD/<task>.py layout"},
}

// shellCands は completion サブコマンドが対応するシェル (説明付き)。
var shellCands = []Candidate{
	{"bash", "print bash completion script"},
	{"zsh", "print zsh completion script"},
	{"fish", "print fish completion script"},
}

// configSubCands は `atcoder config` の sub-subcommand 候補 (ソート済み、説明付き)。
var configSubCands = []Candidate{
	{"get", "print one setting"},
	{"path", "print the config file path"},
	{"set", "change one setting"},
	{"show", "print all settings"},
}

// subcommandCands は補完対象のサブコマンド名 (説明付き)。__complete は隠すので含めない。
var subcommandCands = []Candidate{
	{"new", "scaffold today's exercise dir (or an abc contest)"},
	{"test", "run a solution against downloaded samples"},
	{"run", "run a solution on ad-hoc stdin"},
	{"submit", "open the AtCoder submission page"},
	{"login", "log in to AtCoder and save a session"},
	{"logout", "delete the saved AtCoder session"},
	{"status", "show the judge verdict of your submission"},
	{"stats", "show daily practice statistics"},
	{"config", "show or change tool settings"},
	{"commit", "git-commit today's exercise solutions"},
	{"completion", "print a shell completion script"},
}

// valueFlags は値を 1 つ取るフラグ (次トークンがその値になる)。位置引数の判定で
// 値トークンを読み飛ばすのに使う。
var valueFlags = map[string]bool{
	"--task": true, "--tasks": true, "--layout": true, "--timeout": true,
	"--case": true, "-c": true, "--in": true, "-i": true,
	"--out": true, "-o": true, "--jobs": true, "-j": true,
	"--tolerance": true, "--last": true, "-l": true,
	"--user": true, "--interval": true,
}

// subFlags は各サブコマンドのフラグ候補 (説明付き)。cmd/atcoder/*.go の実フラグ・
// help 文字列と一致させる (フラグを足したらここも更新する)。短形と長形は同じ説明。
var subFlags = map[string][]Candidate{
	"new": {
		{"--tasks", "limit to these tasks (e.g. a,b)"},
		{"--refresh", "force refetch sample cases"},
		{"--no-skeleton", "do not generate skeleton files"},
		{"--no-fetch", "skip all network fetches"},
	},
	"test": {
		{"--task", "task ID or short letter (e.g. d)"},
		{"--refresh", "force refetch sample cases"},
		{"--timeout", "override time limit (e.g. 5s)"},
		{"--case", "run only the given case(s)"},
		{"-c", "run only the given case(s)"},
		{"--layout", "solution file layout"},
		{"--jobs", "parallel test-case workers"},
		{"-j", "parallel test-case workers"},
		{"--watch", "re-run on file change (needs a TTY)"},
		{"-w", "re-run on file change (needs a TTY)"},
		{"-v", "show input/output for each case"},
		{"--verbose", "show input/output for each case"},
		{"-d", "run with DEBUG=1, filter [DEBUG] lines"},
		{"--debug", "run with DEBUG=1, filter [DEBUG] lines"},
		{"-s", "show diff side-by-side"},
		{"--side-by-side", "show diff side-by-side"},
		{"--tolerance", "float comparison tolerance (e.g. 1e-9)"},
	},
	"run": {
		{"--task", "task ID or short letter (e.g. d)"},
		{"--in", "input file ('-' or omit = stdin)"},
		{"-i", "input file ('-' or omit = stdin)"},
		{"--out", "expected output file to judge against"},
		{"-o", "expected output file to judge against"},
		{"--interactive", "interactive mode (live I/O; chat TUI on a TTY)"},
		{"-I", "interactive mode (live I/O; chat TUI on a TTY)"},
		{"--timeout", "override time limit (e.g. 5s)"},
		{"-v", "also show the fed input"},
		{"--verbose", "also show the fed input"},
		{"-d", "run with DEBUG=1, split [DEBUG] lines"},
		{"--debug", "run with DEBUG=1, split [DEBUG] lines"},
		{"--layout", "solution file layout"},
		{"--tolerance", "float comparison tolerance (e.g. 1e-9)"},
	},
	"submit": {
		{"--task", "task ID or short letter (e.g. d)"},
		{"--refresh", "force refetch sample cases"},
		{"--layout", "solution file layout"},
		{"--no-open", "do not open the page in a browser"},
	},
	"stats": {
		{"--week", "limit to this week"},
		{"-w", "limit to this week"},
		{"--month", "limit to this month"},
		{"-m", "limit to this month"},
		{"--year", "limit to this year"},
		{"-y", "limit to this year"},
		{"--last", "rolling window from today (e.g. 7d, 1m)"},
		{"-l", "rolling window from today (e.g. 7d, 1m)"},
		{"--graph", "render time series as a contribution graph"},
		{"-g", "render time series as a contribution graph"},
	},
	"login": {
		{"--user", "AtCoder username (prompts if omitted)"},
		{"--password-stdin", "read the password from stdin (non-interactive)"},
	},
	"logout": nil,
	"status": {
		{"--task", "task ID or short letter (e.g. d)"},
		{"--watch", "poll until the verdict is final (needs a TTY)"},
		{"-w", "poll until the verdict is final (needs a TTY)"},
		{"--interval", "polling interval for --watch (min 2s)"},
		{"--open", "open the submission page in a browser"},
	},
}

// takesContest はそのサブコマンドが <contest> 位置引数を取るか。
var takesContest = map[string]bool{"test": true, "run": true, "submit": true, "status": true}

// Subcommands は補完対象のサブコマンド名を返す (__complete は隠すので含めない)。
func Subcommands() []string {
	return values(subcommandCands)
}

// Flags は指定サブコマンドのフラグ候補を返す。未知サブコマンドは nil。
func Flags(sub string) []string {
	return values(subFlags[sub])
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
// 候補 (説明付き) を返す。__complete の本体。決して error を返さない。
func Complete(root string, words []string) []Candidate {
	if len(words) == 0 {
		return subcommandCands
	}
	cur := words[len(words)-1]

	// サブコマンド位置。
	if len(words) == 1 {
		return filterPrefix(subcommandCands, cur)
	}
	sub := words[0]

	// 値を取るフラグの直後。
	if len(words) >= 2 {
		switch words[len(words)-2] {
		case "--task":
			if c := contestOf(sub, positionals(words)); c != "" {
				return filterPrefix(plain(Tasks(root, c)), cur)
			}
			return nil
		case "--layout":
			return filterPrefix(layoutCands, cur)
		}
	}

	// completion の shell 引数。
	if sub == "completion" {
		return filterPrefix(shellCands, cur)
	}

	// config の sub-subcommand / キー / 値。
	if sub == "config" {
		pos := positionals(words[:len(words)-1])
		switch {
		case len(pos) == 0:
			return filterPrefix(configSubCands, cur)
		case len(pos) == 1 && (pos[0] == "get" || pos[0] == "set"):
			return filterPrefix(plain(config.Keys()), cur)
		case len(pos) == 2 && pos[0] == "set":
			return filterPrefix(plain(config.ValueCandidates(pos[1])), cur)
		}
		return nil
	}

	// フラグ補完。
	if strings.HasPrefix(cur, "-") {
		return filterPrefix(subFlags[sub], cur)
	}

	// 位置引数の補完。cur を除いた既出の位置引数で判定する。
	posBefore := positionals(words[:len(words)-1])
	switch {
	case sub == "new":
		if len(posBefore) == 0 {
			return filterPrefix([]Candidate{{"abc", "prepare an abc contest"}}, cur) // モード名
		}
		if len(posBefore) == 1 && posBefore[0] == "abc" {
			return filterPrefix(plain(Contests(root)), cur)
		}
	case takesContest[sub]:
		if len(posBefore) == 0 {
			return filterPrefix(plain(Contests(root)), cur)
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

// filterPrefix は Value が prefix で前方一致する候補だけを残す (順序保存)。
func filterPrefix(cands []Candidate, prefix string) []Candidate {
	var out []Candidate
	for _, c := range cands {
		if strings.HasPrefix(c.Value, prefix) {
			out = append(out, c)
		}
	}
	return out
}

// plain は説明なしの値スライスを Candidate スライスに包む (動的候補用)。
func plain(values []string) []Candidate {
	out := make([]Candidate, len(values))
	for i, v := range values {
		out[i] = Candidate{Value: v}
	}
	return out
}

// values は Candidate スライスから Value だけを取り出す。
func values(cands []Candidate) []string {
	if cands == nil {
		return nil
	}
	out := make([]string, len(cands))
	for i, c := range cands {
		out[i] = c.Value
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
