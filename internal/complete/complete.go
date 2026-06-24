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
	"github.com/cry999/atcoder-daily-training/internal/cliargs"
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

// categoryCands は `atcoder review` の <category> 位置引数候補 (説明付き)。
var categoryCands = []Candidate{
	{"abc", "AtCoder Beginner Contest"},
	{"arc", "AtCoder Regular Contest"},
	{"agc", "AtCoder Grand Contest"},
	{"ahc", "AtCoder Heuristic Contest"},
	{"awc", "AtCoder Working-system Contest"},
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
	{"unset", "remove a setting or alias"},
}

// subcommandCands は補完対象のサブコマンド名 (説明付き)。__complete は隠すので含めない。
var subcommandCands = []Candidate{
	{"new", "scaffold today's exercise dir (or an abc contest)"},
	{"start", "create the solution file and launch test --watch"},
	{"test", "run a solution (samples by default; --in/--out/--interactive for ad-hoc; --submit to submit)"},
	{"meta", "download / show / edit cached samples + time limit (accepts a task URL)"},
	{"stats", "show daily practice statistics"},
	{"review", "list practiced contests of a category"},
	{"config", "show or change tool settings"},
	{"commit", "git-commit today's exercise solutions"},
	{"completion", "print a shell completion script"},
	{"update", "update atcoder to the latest version"},
	{"version", "print the installed atcoder version"},
}

// 値を取るフラグ (next トークンが値) の集合は internal/cliargs に一本化している。
// 位置引数の判定 (positionals) はそれを共有する。

// subFlags は各サブコマンドのフラグ候補 (説明付き)。cmd/atcoder/*.go の実フラグ・
// help 文字列と一致させる (フラグを足したらここも更新する)。短形と長形は同じ説明。
var subFlags = map[string][]Candidate{
	"new": {
		{"--tasks", "limit to these tasks (e.g. a,b)"},
		{"--refresh", "force refetch sample cases"},
		{"--no-skeleton", "do not generate skeleton files"},
		{"--no-fetch", "skip all network fetches"},
	},
	"start": {
		{"--task", "task ID or short letter (e.g. d)"},
		{"--until-pass", "exit when all sample tests pass"},
		{"--refresh", "force refetch sample cases on the first run"},
		{"--timeout", "override time limit (e.g. 5s)"},
		{"--tolerance", "float comparison tolerance (e.g. 1e-9)"},
		{"-d", "run with DEBUG=1, special-case [DEBUG] lines"},
		{"--debug", "run with DEBUG=1, special-case [DEBUG] lines"},
		{"-s", "show diff side-by-side"},
		{"--side-by-side", "show diff side-by-side"},
		{"--jobs", "parallel test-case workers"},
		{"-j", "parallel test-case workers"},
		{"--layout", "solution file layout"},
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
		{"--in", "ad-hoc input file ('-' = stdin); switches to ad-hoc mode"},
		{"-i", "ad-hoc input file ('-' = stdin); switches to ad-hoc mode"},
		{"--out", "judge a single ad-hoc run against this expected output"},
		{"-o", "judge a single ad-hoc run against this expected output"},
		{"--interactive", "interactive mode (live I/O; chat TUI on a TTY)"},
		{"-I", "interactive mode (live I/O; chat TUI on a TTY)"},
		{"--auto-restart", "with --interactive: re-run each time the child exits"},
		{"-R", "with --interactive: re-run each time the child exits"},
		{"--submit", "after all samples pass, copy + open the submit page"},
		{"--no-open", "with --submit, print the URL instead of opening a browser"},
		{"--keep-debug", "with --submit, copy as-is without commenting out [DEBUG] print lines"},
		{"--json", "print the sample-judging result as JSON (sample mode only)"},
	},
	"meta": {
		{"--task", "task ID or short letter (e.g. d); unneeded when a task URL is given"},
		{"--url", "with set: override the fetch URL for this slot (e.g. abc111 D = arc103_b)"},
		{"--time-limit", "with set: override the cached time limit (e.g. 5s)"},
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
	"review": {
		{"--week", "limit to this week"},
		{"-w", "limit to this week"},
		{"--month", "limit to this month"},
		{"-m", "limit to this month"},
		{"--year", "limit to this year"},
		{"-y", "limit to this year"},
		{"--last", "rolling window from today (e.g. 7d, 1m)"},
		{"-l", "rolling window from today (e.g. 7d, 1m)"},
	},
	"update": {
		{"--check", "only check for a newer version; don't install"},
		{"--local", "install from the local ./cmd/atcoder working tree"},
	},
}

// takesContest はそのサブコマンドが <contest> 位置引数を取るか。
var takesContest = map[string]bool{"start": true, "test": true}

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
		return subcommandCandidates()
	}
	cur := words[len(words)-1]

	// サブコマンド位置。組み込み + config の alias を候補にする。
	if len(words) == 1 {
		return filterPrefix(subcommandCandidates(), cur)
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
		case len(pos) == 1 && (pos[0] == "get" || pos[0] == "set" || pos[0] == "unset"):
			return filterPrefix(plain(configKeys()), cur)
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
	case sub == "review":
		if len(posBefore) == 0 {
			return filterPrefix(categoryCands, cur)
		}
	}
	return nil
}

// positionals は sub を除いたトークン列から位置引数だけを抜き出す。フラグ (- 始まり)
// と、値を取るフラグの直後のトークンは読み飛ばす。
// positionals は words からサブコマンド (words[0]) を除いた位置引数を返す。
// フラグ/値の分離は cliargs.Split に委譲する (value-flag 知識を一本化)。
func positionals(words []string) []string {
	if len(words) == 0 {
		return nil
	}
	_, pos := cliargs.Split(words[1:]) // words[0] = サブコマンド
	return pos
}

// contestOf は位置引数列から確定済みの contest_id を取り出す。
func contestOf(sub string, pos []string) string {
	switch sub {
	case "new":
		if len(pos) >= 2 && pos[0] == "abc" {
			return pos[1]
		}
	case "test", "start":
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

// subcommandCandidates は組み込みサブコマンドに config の alias を足した候補を返す。
func subcommandCandidates() []Candidate {
	return append(append([]Candidate{}, subcommandCands...), aliasCands()...)
}

// aliasCands は config の [alias] を補完候補にする (説明は展開先)。組み込みと
// 同名の alias は dispatch で無視されるので候補から除く。config エラーは無視。
func aliasCands() []Candidate {
	aliases, err := config.Aliases()
	if err != nil || len(aliases) == 0 {
		return nil
	}
	builtin := make(map[string]bool, len(subcommandCands))
	for _, c := range subcommandCands {
		builtin[c.Value] = true
	}
	names := make([]string, 0, len(aliases))
	for n := range aliases {
		if !builtin[n] {
			names = append(names, n)
		}
	}
	sort.Strings(names)
	out := make([]Candidate, 0, len(names))
	for _, n := range names {
		out = append(out, Candidate{Value: n, Desc: "alias → " + aliases[n]})
	}
	return out
}

// configKeys は config の typed キーに既存 alias キー (alias.<name>) を足して返す
// (get/set/unset のキー補完用)。AliasKeys のエラーは無視。
func configKeys() []string {
	keys := config.Keys()
	if ak, err := config.AliasKeys(); err == nil {
		keys = append(keys, ak...)
	}
	return keys
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
