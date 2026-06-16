// Package chatlog はインタラクティブ chat で子 (解答プログラム) へ送った入力行を、
// 問題 (contest+task) ごとにローカル (データ領域) へ JSONL で追記し、前回セッションの
// 入力を読み戻す。目的は `:replay` (要件 039) による「前回と同じ入力の再実行」で、
// ネットワークには一切出さない。記録は best-effort で、失敗しても chat 本体に影響
// させない (呼び出し側が error を無視する non-fatal 設計)。永続化の規約は利用統計
// internal/usagelog (要件 037) を踏襲する。
package chatlog

import (
	"bufio"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// AppName はデータ領域のアプリ識別子 (internal/cachepath / usagelog と揃える)。
const AppName = "atcoder-tools"

// DisableEnv が非空なら記録を完全にスキップする (前回入力は常に空になる)。
const DisableEnv = "ATCODER_NO_CHAT_HISTORY"

// Event は子へ送った 1 入力行の記録 (JSONL 1 行)。
type Event struct {
	TS      time.Time `json:"ts"`
	Session string    `json:"session"` // chat 起動ごとの一意 ID。同一 session の行が 1 セッション分
	Text    string    `json:"text"`    // 子 stdin へ送った 1 行 (空行も保存する)
}

// dataBase は XDG_DATA_HOME (未設定なら ~/.local/share、最終 fallback ./.local/share)。
// キャッシュ (cachepath) と違い、入力履歴はユーザ由来で再生成不能なので消えない領域に置く。
func dataBase() string {
	if d := os.Getenv("XDG_DATA_HOME"); d != "" {
		return d
	}
	if home, err := os.UserHomeDir(); err == nil {
		return filepath.Join(home, ".local", "share")
	}
	return filepath.Join(".local", "share")
}

// Dir は chat 入力履歴のルートディレクトリ ($XDG_DATA_HOME/atcoder-tools/chat-history)。
func Dir() string { return filepath.Join(dataBase(), AppName, "chat-history") }

// Path は問題 (contest, task) の JSONL の絶対パス (Dir/<contest>/<task>.jsonl)。
// contest/task はパス区切りを潰してディレクトリ外への脱出を防ぐ。
func Path(contest, task string) string {
	return filepath.Join(Dir(), sanitize(contest), sanitize(task)+".jsonl")
}

// sanitize はパス成分から区切り文字を除去する (識別子をファイル名に使うため)。
func sanitize(s string) string {
	s = strings.ReplaceAll(s, "/", "-")
	s = strings.ReplaceAll(s, string(filepath.Separator), "-")
	return s
}

// Disabled は ATCODER_NO_CHAT_HISTORY が非空かを返す。
func Disabled() bool { return os.Getenv(DisableEnv) != "" }

// NewSessionID は chat 起動ごとの一意なセッション ID を返す (時刻ベース)。
// 人間の操作間隔ではナノ秒精度で衝突しない。
func NewSessionID() string { return time.Now().Format("20060102T150405.000000000") }

// Record は 1 入力行を問題ごとの JSONL に追記する。Disabled / 空キーなら何もしない。
// 失敗時は error を返すが、呼び出し側 (chat の RecordInput フック) は無視する (non-fatal)。
func Record(contest, task, session, text string) error {
	if Disabled() || contest == "" || task == "" {
		return nil
	}
	path := Path(contest, task)
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	line, err := json.Marshal(Event{TS: time.Now(), Session: session, Text: text})
	if err != nil {
		return err
	}
	f, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()
	_, err = f.Write(append(line, '\n'))
	return err
}

// LoadLastSession は問題 (contest, task) の JSONL を読み、最後に記録された session の
// 入力行を出現順 (= 送信順) で返す。ファイルが無い・空キー・Disabled・壊れ行は
// best-effort に扱い、該当が無ければ空スライスを返す。
func LoadLastSession(contest, task string) ([]string, error) {
	if contest == "" || task == "" {
		return nil, nil
	}
	f, err := os.Open(Path(contest, task))
	if err != nil {
		if os.IsNotExist(err) {
			return nil, nil // まだ履歴が無い
		}
		return nil, err
	}
	defer f.Close()

	// 全イベントを順序保持で読み込み、最後の session を特定してその text を集める。
	var events []Event
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 0, 64*1024), 1024*1024) // 長い行に備える
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if line == "" {
			continue
		}
		var ev Event
		if err := json.Unmarshal([]byte(line), &ev); err != nil {
			continue // 壊れ行はスキップ (best-effort)
		}
		events = append(events, ev)
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}
	if len(events) == 0 {
		return nil, nil
	}
	last := events[len(events)-1].Session
	out := make([]string, 0, len(events))
	for _, ev := range events {
		if ev.Session == last {
			out = append(out, ev.Text)
		}
	}
	return out, nil
}
