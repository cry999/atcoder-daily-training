// Package layout は解答ファイル配置規約を Strategy パターンで表現する。
//
// test / run コマンドは contest_id と task から解答ファイルパスを得るために
// Layout インターフェースを使う。各レイアウトは ABC / Exercise などの struct
// として実装され、test/run はその中身を知らない。レイアウト追加 (ARC/AGC など)
// は新しい struct を追加するだけで、既存コードに触れずに済む (open-closed)。
//
// task_id / letter の抽出は layout に依存しないので、package トップレベルの
// 関数として分離してある (cache key・AtCoder URL でも同じ値が必要なため)。
package layout

import (
	"fmt"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

// Layout は解答ファイル配置規約。
type Layout interface {
	// Name はフラグ値や診断メッセージ用のレイアウト識別子 ("abc" / "exercise" 等)。
	Name() string

	// SolutionPath はリポジトリルートからの相対パスを返す。
	// contestID は AtCoder の contest ID (例: "abc457")、
	// task は letter 単体 ("d") か AtCoder の task ID ("abc457_d") のどちらでもよい。
	SolutionPath(contestID, task string) (string, error)
}

// abcContestRE は abc<NNN> 形式 (NNN は数字 1 文字以上) を捕捉する。
var abcContestRE = regexp.MustCompile(`^abc(\d+)$`)

// ContestNum は abc<NNN> 形式の contest ID から数字部分 (例: "457") を取り出す。
// ABC レイアウトのディレクトリ名 (`abc/<contest_num>/`) に使う。
// abc<NNN> 形式でなければ ok=false を返す。
func ContestNum(contestID string) (string, bool) {
	m := abcContestRE.FindStringSubmatch(contestID)
	if m == nil {
		return "", false
	}
	return m[1], true
}

// TaskID は短縮形 task ("d") を AtCoder の task ID ("abc457_d") に展開する。
// 既に `_` を含んでいればそのまま返す (例: "abc457_d" → "abc457_d")。
// layout に依存しない (cache key / AtCoder URL 共通)。
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

// ABC は `abc/<contest_num>/<letter>.py` 配置のレイアウト。
type ABC struct{}

func (ABC) Name() string { return "abc" }

func (ABC) SolutionPath(contestID, task string) (string, error) {
	m := abcContestRE.FindStringSubmatch(contestID)
	if m == nil {
		return "", fmt.Errorf("abc layout requires contest ID like abc<NNN>, got %q", contestID)
	}
	contestNum := m[1]
	letter, err := Letter(task)
	if err != nil {
		return "", fmt.Errorf("abc layout: %w", err)
	}
	return filepath.Join("abc", contestNum, letter+".py"), nil
}

// Exercise は `exercise/YYYY/MM/DD/<task_id>.py` 配置のレイアウト (練習用)。
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

// Parse は CLI フラグ値と contest_id から Layout を選ぶ。
//   - "" / "auto" → Detect(contestID)
//   - "abc"       → ABC{}
//   - "exercise"  → Exercise{}
//   - その他      → エラー
func Parse(name, contestID string) (Layout, error) {
	switch name {
	case "", "auto":
		return Detect(contestID), nil
	case "abc":
		return ABC{}, nil
	case "exercise":
		return Exercise{}, nil
	default:
		return nil, fmt.Errorf("unknown layout %q (must be auto, abc, or exercise)", name)
	}
}

// Detect は contest_id から layout を自動選択する純粋関数。
// `abc<NNN>` にマッチすれば ABC、それ以外は Exercise。
func Detect(contestID string) Layout {
	if abcContestRE.MatchString(contestID) {
		return ABC{}
	}
	return Exercise{}
}
