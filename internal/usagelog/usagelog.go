// Package usagelog はサブコマンド利用イベントをローカル (データ領域) に JSONL で
// 追記し、コマンド別に集計する。目的は実利用データに基づくコマンド設計の判断で、
// ネットワークには一切出さない。記録は best-effort で、失敗してもコマンド本体に
// 影響させない (呼び出し側が error を無視する non-fatal 設計)。要件 037。
package usagelog

import (
	"bufio"
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// AppName はデータ領域のアプリ識別子 (internal/cachepath と揃える)。
const AppName = "atcoder-tools"

// DisableEnv が非空なら記録を完全にスキップする。
const DisableEnv = "ATCODER_NO_USAGE"

// Event は 1 回のサブコマンド実行の記録 (JSONL 1 行)。
type Event struct {
	TS      time.Time `json:"ts"`
	Cmd     string    `json:"cmd"`
	Flags   []string  `json:"flags"`
	DurMs   int64     `json:"dur_ms"`
	Exit    int       `json:"exit"`
	Version string    `json:"version"`
}

// dataBase は XDG_DATA_HOME (未設定なら ~/.local/share、最終 fallback ./.local/share)。
// キャッシュ (cachepath) と違い、利用履歴は集計の材料なので消えない領域に置く。
func dataBase() string {
	if d := os.Getenv("XDG_DATA_HOME"); d != "" {
		return d
	}
	if home, err := os.UserHomeDir(); err == nil {
		return filepath.Join(home, ".local", "share")
	}
	return filepath.Join(".local", "share")
}

// Dir は利用ログのディレクトリ ($XDG_DATA_HOME/atcoder-tools/usage)。
func Dir() string { return filepath.Join(dataBase(), AppName, "usage") }

// Path は events.jsonl の絶対パス。
func Path() string { return filepath.Join(Dir(), "events.jsonl") }

// Disabled は ATCODER_NO_USAGE が非空かを返す。
func Disabled() bool { return os.Getenv(DisableEnv) != "" }

// Record は 1 イベントを JSONL に追記する。Disabled なら何もしない。
// 失敗時は error を返すが、呼び出し側 (main) は無視する (non-fatal)。
func Record(ev Event) error {
	if Disabled() {
		return nil
	}
	if err := os.MkdirAll(Dir(), 0o755); err != nil {
		return err
	}
	line, err := json.Marshal(ev)
	if err != nil {
		return err
	}
	f, err := os.OpenFile(Path(), os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()
	// 1 行ずつ追記 (O_APPEND)。複数プロセス同時実行でも行は混ざりにくい。
	_, err = f.Write(append(line, '\n'))
	return err
}

// FlagsFromArgs は引数列から「使われたフラグ名」を抜く (正規化 + 重複除去)。
//   - "-"/"--" で始まるトークンのみ対象 (値や位置引数は捨てる)。
//   - 先頭のダッシュを除き、"=value" は手前まで ("--last=3d" → "last")。
//   - 単独 "-" (stdin マーカー) は空になるので捨てる。
//   - 出現順を保ったまま重複を除く。
func FlagsFromArgs(args []string) []string {
	var out []string
	seen := map[string]bool{}
	for _, a := range args {
		if !strings.HasPrefix(a, "-") {
			continue // 値・位置引数
		}
		name := strings.TrimLeft(a, "-")
		if i := strings.IndexByte(name, '='); i >= 0 {
			name = name[:i]
		}
		if name == "" || seen[name] {
			continue
		}
		seen[name] = true
		out = append(out, name)
	}
	return out
}

// Stat は 1 コマンドの集計結果。
type Stat struct {
	Cmd     string
	Count   int
	TotalMs int64
	Last    time.Time
	Flags   map[string]int // フラグ名 → 回数 (--flags 用)
}

// AvgMs は 1 回あたりの平均所要時間 (ms)。Count==0 なら 0。
func (s Stat) AvgMs() int64 {
	if s.Count == 0 {
		return 0
	}
	return s.TotalMs / int64(s.Count)
}

// Aggregate は JSONL を読み、cmd 別に集計して count 降順 (同数は cmd 名昇順) で返す。
// 壊れた行 (パース失敗) はスキップする (集計は best-effort)。
func Aggregate(r io.Reader) ([]Stat, error) {
	byCmd := map[string]*Stat{}
	sc := bufio.NewScanner(r)
	sc.Buffer(make([]byte, 0, 64*1024), 1024*1024) // 長い行に備える
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if line == "" {
			continue
		}
		var ev Event
		if err := json.Unmarshal([]byte(line), &ev); err != nil {
			continue // 壊れ行はスキップ
		}
		if ev.Cmd == "" {
			continue
		}
		s := byCmd[ev.Cmd]
		if s == nil {
			s = &Stat{Cmd: ev.Cmd, Flags: map[string]int{}}
			byCmd[ev.Cmd] = s
		}
		s.Count++
		s.TotalMs += ev.DurMs
		if ev.TS.After(s.Last) {
			s.Last = ev.TS
		}
		for _, fl := range ev.Flags {
			s.Flags[fl]++
		}
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}
	out := make([]Stat, 0, len(byCmd))
	for _, s := range byCmd {
		out = append(out, *s)
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].Count != out[j].Count {
			return out[i].Count > out[j].Count
		}
		return out[i].Cmd < out[j].Cmd
	})
	return out, nil
}
