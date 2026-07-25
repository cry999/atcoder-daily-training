// Package mode は解答ファイル配置規約を Strategy パターンで表現する。
//
// test / start / record コマンドは contest_id と task から解答ファイルパスを
// 得るために Mode インターフェースを使う。配置規約は contest / exercise の 2 種で、
// contest は <prefix>/<contest_num>/<letter>.py、exercise は
// exercise/YYYY/MM/DD/<task_id>.py に解決する。
//
// task_id / letter の抽出は mode に依存しないので、package トップレベルの関数
// として分離してある (cache key・AtCoder URL でも同じ値が必要なため)。
package mode

import (
	"errors"
	"fmt"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// Mode は解答ファイル配置規約。
type Mode interface {
	// Name はフラグ値や診断メッセージ用の配置識別子 ("contest" / "exercise")。
	Name() string

	// SolutionPath はリポジトリルートからの相対パスを返す。
	// contestID は AtCoder の contest ID (例: "abc457")、
	// task は letter 単体 ("d") か AtCoder の task ID ("abc457_d") のどちらでもよい。
	SolutionPath(contestID, task string) (string, error)
}

// contestIDRE は <英字接頭辞><数字> 形式の contest_id を接頭辞と数字に分ける。
var contestIDRE = regexp.MustCompile(`^([A-Za-z]+)(\d+)$`)

// SplitContestID は contest_id を英字接頭辞と数字に分ける。
// 例: "abc457" → ("abc", "457", true) / "arc100" → ("arc", "100", true)。
// 形式 (<英字接頭辞><数字>) に一致しなければ ok=false。
func SplitContestID(id string) (prefix, num string, ok bool) {
	m := contestIDRE.FindStringSubmatch(id)
	if m == nil {
		return "", "", false
	}
	return strings.ToLower(m[1]), m[2], true
}

// ナビゲーション (ShiftLetter / ShiftContest) の境界・形式エラー。
// UI 向けの日本語文言は別レイヤで被せる前提なので、ここは汎用の英語メッセージ。
var (
	ErrLetterShape  = errors.New("letter is not a single a..z")
	ErrLetterBound  = errors.New("letter is out of range")
	ErrContestShape = errors.New("contest id has no numeric suffix")
	ErrContestBound = errors.New("contest number is out of range")
)

// ShiftLetter は単一文字 letter を delta だけずらす。
//   - ("d", +1) → "e" / ("d", -1) → "c"
//
// letter が単一の a..z 1 文字でなければ ErrLetterShape (空・複数文字・非英字)。
// 結果が 'a' 未満 / 'z' 超なら ErrLetterBound。
func ShiftLetter(letter string, delta int) (string, error) {
	if len(letter) != 1 || letter[0] < 'a' || letter[0] > 'z' {
		return "", ErrLetterShape
	}
	n := int(letter[0]-'a') + delta
	if n < 0 || n > 25 {
		return "", ErrLetterBound
	}
	return string(rune('a' + n)), nil
}

// ShiftContest は <英字接頭辞><数字> 形式の contest_id の数字部を delta だけずらす。
//   - ("abc457", +1) → "abc458" / ("abc457", -1) → "abc456"
//
// ゼロ詰め幅は元の桁数を下限に保持 (abc099 → abc100)。形式に一致しなければ
// ErrContestShape、数字が 1 未満になるなら ErrContestBound。
func ShiftContest(contestID string, delta int) (string, error) {
	prefix, num, ok := SplitContestID(contestID)
	if !ok {
		return "", ErrContestShape
	}
	n, _ := strconv.Atoi(num)
	n += delta
	if n < 1 {
		return "", ErrContestBound
	}
	return fmt.Sprintf("%s%0*d", prefix, len(num), n), nil
}

// WithContestNum は <英字接頭辞><数字> 形式の contest_id の数字部を n に**絶対設定**する
// (chat ナビの直指定 `:contest <num>` 用)。接頭辞と元の桁数 (ゼロ詰め幅の下限) を保つ。
//   - ("abc457", 123) → "abc123" / ("abc457", 5) → "abc005"
//
// 形式に一致しなければ ErrContestShape、n が 1 未満なら ErrContestBound。
func WithContestNum(contestID string, n int) (string, error) {
	prefix, num, ok := SplitContestID(contestID)
	if !ok {
		return "", ErrContestShape
	}
	if n < 1 {
		return "", ErrContestBound
	}
	return fmt.Sprintf("%s%0*d", prefix, len(num), n), nil
}

// TaskID は短縮形 task ("d") を AtCoder の task ID ("abc457_d") に展開する。
// 既に `_` を含んでいればそのまま返す (例: "abc457_d" → "abc457_d")。
// mode に依存しない (cache key / AtCoder URL 共通)。
func TaskID(contestID, task string) string {
	if strings.Contains(task, "_") {
		return task
	}
	return contestID + "_" + task
}

// Letter は task から末尾の letter を取り出す。
//   - "d"         → "d"
//   - "abc457_d"  → "d"
//   - "abc457_xy" → "xy" (将来 H+ の複数文字 letter にも備える)
//
// 抽出した letter は **小文字** に正規化される。
func Letter(task string) (string, error) {
	if task == "" {
		return "", fmt.Errorf("task is empty")
	}
	if i := strings.LastIndex(task, "_"); i >= 0 {
		tail := task[i+1:]
		if tail == "" {
			return "", fmt.Errorf("task %q has empty letter after '_'", task)
		}
		return strings.ToLower(tail), nil
	}
	return strings.ToLower(task), nil
}

// taskURLRe は AtCoder の task ページ URL から contest_id / task_id を捕捉する。
// スキーム (https?://) の有無を問わず、クエリ (?lang=ja) やフラグメントが続いても
// `/contests/<contest>/tasks/<task>` の部分だけを取り出す。
var taskURLRe = regexp.MustCompile(`atcoder\.jp/contests/([^/]+)/tasks/([^/?#]+)`)

// ParseTaskURL は AtCoder の task ページ URL から contest_id / task_id を抽出する。
//   - "https://atcoder.jp/contests/abc457/tasks/abc457_d" → ("abc457", "abc457_d", true)
//   - "atcoder.jp/contests/abc457/tasks/abc457_d?lang=ja"  → ("abc457", "abc457_d", true)
//
// `/contests/.../tasks/...` を取り出せなければ ok=false。mode に依存しない
// (cache key / AtCoder URL 共通の ID 抽出ヘルパー)。
func ParseTaskURL(s string) (contestID, taskID string, ok bool) {
	m := taskURLRe.FindStringSubmatch(s)
	if m == nil {
		return "", "", false
	}
	return m[1], m[2], true
}

// IsTaskURL は s を task URL とみなすか判定する (`://` を含む or `atcoder.jp/` を含む)。
// 位置引数が contest_id か URL かを切り分けるための緩いヒューリスティック。
func IsTaskURL(s string) bool {
	return strings.Contains(s, "://") || strings.Contains(s, "atcoder.jp/")
}

// Contest は `<prefix>/<contest_num>/<letter>.py` 配置の mode。
type Contest struct{}

func (Contest) Name() string { return "contest" }

func (Contest) SolutionPath(contestID, task string) (string, error) {
	prefix, num, ok := SplitContestID(contestID)
	if !ok {
		return "", fmt.Errorf("contest id must be <prefix><num>, got %q", contestID)
	}
	letter, err := Letter(task)
	if err != nil {
		return "", fmt.Errorf("contest mode: %w", err)
	}
	return filepath.Join(prefix, num, letter+".py"), nil
}

// Exercise は `exercise/YYYY/MM/DD/<task_id>.py` 配置の mode (練習用)。
// Today はゼロ値なら time.Now().Local() を使う (テスト時に固定したい場合に注入)。
type Exercise struct {
	Today time.Time
}

func (Exercise) Name() string { return "exercise" }

func (e Exercise) SolutionPath(contestID, task string) (string, error) {
	t := e.Today
	if t.IsZero() {
		t = time.Now().Local()
	}
	y, m, d := t.Date()
	return filepath.Join(
		"exercise",
		fmt.Sprintf("%04d", y),
		fmt.Sprintf("%02d", m),
		fmt.Sprintf("%02d", d),
		TaskID(contestID, task)+".py",
	), nil
}

// Parse は CLI フラグ値から Mode を選ぶ。
//   - "" / "exercise" → Exercise{}
//   - "contest"       → Contest{}
//   - その他          → エラー
func Parse(name string) (Mode, error) {
	switch name {
	case "", "exercise":
		return Exercise{}, nil
	case "contest":
		return Contest{}, nil
	default:
		return nil, fmt.Errorf("unknown mode %q (must be contest or exercise)", name)
	}
}

// Names は既知 mode 名を正規順 (contest, exercise) で返す。
// 検証 (Known) と補完候補・config の値候補がここを単一情報源とすることで、
// 受理される mode 名の一覧を二重管理しないで済む。
func Names() []string {
	return []string{"contest", "exercise"}
}

// Known は mode 名が既知 (contest/exercise) かを返す (config set の検証用)。
func Known(name string) bool {
	for _, n := range Names() {
		if name == n {
			return true
		}
	}
	return false
}

// Resolve は既定 mode の precedence を 1 か所に集約する純粋関数。
// 優先順は flag > env > config > exercise で、最初に空でない値を採用する
// (どれも空なら "exercise")。採用した値を Parse して Mode を返す。
//
// value は採用した mode 名、source はその出所
// ("flag"/"env"/"config"/"default") で、診断に使う。値が未知なら Parse が
// エラーを返す。
func Resolve(flag, env, cfg string) (m Mode, value, source string, err error) {
	switch {
	case flag != "":
		value, source = flag, "flag"
	case env != "":
		value, source = env, "env"
	case cfg != "":
		value, source = cfg, "config"
	default:
		value, source = "exercise", "default"
	}
	m, err = Parse(value)
	if err != nil {
		return nil, value, source, err
	}
	return m, value, source, nil
}
