// Package solvestat は解答ファイル冒頭の機械可読コメントブロック
// (solve-stat ブロック) の読み書きを担う (要件 061)。
//
// ブロックは常にファイル先頭に置かれ、開始/終了マーカーで挟んだ
// 1 行 1 キーのコメント列である:
//
//	# >>> atcoder-stat >>>
//	# started_at  = 2026-07-01T16:00:00+09:00
//	# solved_at   = 2026-07-01T16:25:00+09:00
//	# duration_ms = 1500000
//	# ac          = true
//	# knowledge   = 2
//	# <<< atcoder-stat <<<
//
// Parse / Merge は I/O から分離した純粋関数で、部分更新 (キー単位マージ) と
// ラウンドトリップをユニットテストで固定できるようにしてある。書き込みは
// temp+rename で atomic に行い、途中失敗で解答を壊さない。
package solvestat

import (
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

const (
	startMarker = "# >>> atcoder-stat >>>"
	endMarker   = "# <<< atcoder-stat <<<"

	// commentPrefix はコメント行の先頭。当面 Python の "#" 固定。
	// 将来の言語別対応 (Go/C++ の "//" 等) でここを差し替える (要件 061 前方互換)。
	commentPrefix = "#"

	// keyWidth は key 列の桁揃え幅 (最長キー "duration_ms"/"translation" = 11)。
	keyWidth = 11
)

// Score は 5 軸スコア。各軸 0..3、未記録は -1。
type Score struct {
	Knowledge   int
	Translation int
	Complexity  int
	Impl        int
	Verify      int
}

// Stat は solve-stat ブロックの内容。各フィールドは任意 (未記録判別は下記):
//   - StartedAt/SolvedAt: ゼロ値 (IsZero) が未記録
//   - DurationMs/TargetMs: 0 が未記録
//   - AC/Editorial: nil が未記録
//   - Score 各軸: -1 が未記録
type Stat struct {
	StartedAt  time.Time
	SolvedAt   time.Time
	DurationMs int64
	TargetMs   int64
	AC         *bool
	Editorial  *bool
	Score      Score
}

// Empty は全項目未記録の Stat を返す。patch を組み立てるときの起点に使う
// (Score のゼロ値 {0,0,0,0,0} は「全軸 0 点」と区別できないため、必ず
// Empty() から始めて設定したい軸だけ上書きする)。
func Empty() Stat {
	return Stat{Score: Score{-1, -1, -1, -1, -1}}
}

// BoolPtr は *bool フィールド (AC/Editorial) の設定を簡潔にするヘルパー。
func BoolPtr(b bool) *bool { return &b }

func (s Stat) hasStarted() bool  { return !s.StartedAt.IsZero() }
func (s Stat) hasSolved() bool   { return !s.SolvedAt.IsZero() }
func (s Stat) hasDuration() bool { return s.DurationMs != 0 }
func (s Stat) hasTarget() bool   { return s.TargetMs != 0 }

// Parse は src から solve-stat ブロックを読む。ブロックが無ければ
// (Empty(), false, nil)。マーカーが片方だけ/重複するなど破損している場合は
// error を返す (自動修復しない安全側)。
func Parse(src []byte) (Stat, bool, error) {
	lines := strings.Split(string(src), "\n")
	startIdx, endIdx, startCount, endCount := locateMarkers(lines)
	if startCount == 0 && endCount == 0 {
		return Empty(), false, nil
	}
	if startCount != 1 || endCount != 1 || startIdx > endIdx {
		return Empty(), false, fmt.Errorf("solve-stat ブロックが破損しています (マーカー不整合: 開始 %d 個 / 終了 %d 個)", startCount, endCount)
	}
	st := Empty()
	for _, ln := range lines[startIdx+1 : endIdx] {
		t := strings.TrimSpace(ln)
		if t == "" || !strings.HasPrefix(t, commentPrefix) {
			continue
		}
		body := strings.TrimSpace(strings.TrimPrefix(t, commentPrefix))
		eq := strings.Index(body, "=")
		if eq < 0 {
			continue
		}
		key := strings.TrimSpace(body[:eq])
		val := strings.TrimSpace(body[eq+1:])
		if err := st.setKey(key, val); err != nil {
			return Empty(), false, fmt.Errorf("solve-stat ブロックの %s が不正です: %w", key, err)
		}
	}
	return st, true, nil
}

// Merge は src のブロックへ patch をキー単位で部分マージした新ソースを返す。
// ブロックが無ければ先頭に新規挿入する。src が破損している場合は error。
func Merge(src []byte, patch Stat) ([]byte, error) {
	base, found, err := Parse(src)
	if err != nil {
		return nil, err
	}
	merged := mergeStat(base, patch)
	return spliceBlock(src, renderBlock(merged), found), nil
}

// Strip は src から solve-stat ブロックを取り除いた新ソースを返す。ブロックが無ければ
// src をそのまま返す。マーカーが破損している (片方だけ/重複/順序逆転) 場合は、コードを
// 誤って削らないよう src をそのまま返す (Parse と同じ安全側)。提出される中身から個人の
// 練習メタデータ (solve-stat) を除くのに使う (要件 063)。解答ファイルは書き換えない。
func Strip(src []byte) []byte {
	lines := strings.Split(string(src), "\n")
	startIdx, endIdx, startCount, endCount := locateMarkers(lines)
	if startCount == 0 && endCount == 0 {
		return src // ブロック無し: 無加工 (バイト等価)。
	}
	if startCount != 1 || endCount != 1 || startIdx > endIdx {
		return src // 破損: 誤削除を避け、そのまま返す。
	}
	out := make([]string, 0, len(lines))
	out = append(out, lines[:startIdx]...)
	out = append(out, lines[endIdx+1:]...)
	return []byte(strings.Join(out, "\n"))
}

// Overwrite は既存ブロックを破棄し st だけのブロックへ置き換えた新ソースを返す
// (--restart 用: 前回の完了記録・スコアを捨てて着手からやり直す)。src が破損して
// いる場合は error。
func Overwrite(src []byte, st Stat) ([]byte, error) {
	_, found, err := Parse(src)
	if err != nil {
		return nil, err
	}
	return spliceBlock(src, renderBlock(st), found), nil
}

// spliceBlock は block を src の先頭 (ブロック無し) or 既存ブロック位置 (置換) に差し込む。
func spliceBlock(src []byte, block string, found bool) []byte {
	if !found {
		// 先頭に新規挿入。既存コードはそのまま後ろへ。
		return append([]byte(block), src...)
	}
	lines := strings.Split(string(src), "\n")
	startIdx, endIdx, _, _ := locateMarkers(lines)
	blockLines := strings.Split(strings.TrimRight(block, "\n"), "\n")
	out := make([]string, 0, len(lines)+len(blockLines))
	out = append(out, lines[:startIdx]...)
	out = append(out, blockLines...)
	out = append(out, lines[endIdx+1:]...)
	return []byte(strings.Join(out, "\n"))
}

// ReadFile は path のファイルから Stat を読む。
func ReadFile(path string) (Stat, bool, error) {
	src, err := os.ReadFile(path)
	if err != nil {
		return Empty(), false, err
	}
	return Parse(src)
}

// Update は path のファイルへ patch を部分マージして atomic に書き戻す。
// ファイルが無ければブロックだけの新規ファイルを作る。
func Update(path string, patch Stat) error {
	return update(path, func(src []byte) ([]byte, error) { return Merge(src, patch) })
}

// OverwriteFile は path のファイルのブロックを st で全置換して atomic に書き戻す
// (--restart 用)。
func OverwriteFile(path string, st Stat) error {
	return update(path, func(src []byte) ([]byte, error) { return Overwrite(src, st) })
}

func update(path string, transform func([]byte) ([]byte, error)) error {
	src, err := os.ReadFile(path)
	if err != nil {
		if !os.IsNotExist(err) {
			return err
		}
		src = nil
	}
	out, err := transform(src)
	if err != nil {
		return err
	}
	return atomicWrite(path, out)
}

func locateMarkers(lines []string) (startIdx, endIdx, startCount, endCount int) {
	startIdx, endIdx = -1, -1
	for i, ln := range lines {
		switch strings.TrimSpace(ln) {
		case startMarker:
			startCount++
			if startIdx < 0 {
				startIdx = i
			}
		case endMarker:
			endCount++
			if endIdx < 0 {
				endIdx = i
			}
		}
	}
	return startIdx, endIdx, startCount, endCount
}

func (s *Stat) setKey(key, val string) error {
	switch key {
	case "started_at":
		t, err := time.Parse(time.RFC3339, val)
		if err != nil {
			return err
		}
		s.StartedAt = t
	case "solved_at":
		t, err := time.Parse(time.RFC3339, val)
		if err != nil {
			return err
		}
		s.SolvedAt = t
	case "duration_ms":
		n, err := strconv.ParseInt(val, 10, 64)
		if err != nil {
			return err
		}
		s.DurationMs = n
	case "target_ms":
		n, err := strconv.ParseInt(val, 10, 64)
		if err != nil {
			return err
		}
		s.TargetMs = n
	case "ac":
		b, err := strconv.ParseBool(val)
		if err != nil {
			return err
		}
		s.AC = &b
	case "editorial":
		b, err := strconv.ParseBool(val)
		if err != nil {
			return err
		}
		s.Editorial = &b
	case "knowledge", "translation", "complexity", "impl", "verify":
		n, err := strconv.Atoi(val)
		if err != nil {
			return err
		}
		s.setScore(key, n)
	default:
		// 未知キーは読み飛ばす (前方互換)。
	}
	return nil
}

func (s *Stat) setScore(axis string, n int) {
	switch axis {
	case "knowledge":
		s.Score.Knowledge = n
	case "translation":
		s.Score.Translation = n
	case "complexity":
		s.Score.Complexity = n
	case "impl":
		s.Score.Impl = n
	case "verify":
		s.Score.Verify = n
	}
}

func mergeStat(base, patch Stat) Stat {
	out := base
	if patch.hasStarted() {
		out.StartedAt = patch.StartedAt
	}
	if patch.hasSolved() {
		out.SolvedAt = patch.SolvedAt
	}
	if patch.hasDuration() {
		out.DurationMs = patch.DurationMs
	}
	if patch.hasTarget() {
		out.TargetMs = patch.TargetMs
	}
	if patch.AC != nil {
		out.AC = patch.AC
	}
	if patch.Editorial != nil {
		out.Editorial = patch.Editorial
	}
	if patch.Score.Knowledge >= 0 {
		out.Score.Knowledge = patch.Score.Knowledge
	}
	if patch.Score.Translation >= 0 {
		out.Score.Translation = patch.Score.Translation
	}
	if patch.Score.Complexity >= 0 {
		out.Score.Complexity = patch.Score.Complexity
	}
	if patch.Score.Impl >= 0 {
		out.Score.Impl = patch.Score.Impl
	}
	if patch.Score.Verify >= 0 {
		out.Score.Verify = patch.Score.Verify
	}
	return out
}

// renderBlock は Stat の set 済みキーだけをスキーマ順に整形したブロック文字列
// (末尾改行つき) を返す。key 列は keyWidth に揃える。
func renderBlock(s Stat) string {
	var b strings.Builder
	b.WriteString(startMarker + "\n")
	add := func(key, val string) {
		fmt.Fprintf(&b, "%s %-*s = %s\n", commentPrefix, keyWidth, key, val)
	}
	if s.hasStarted() {
		add("started_at", s.StartedAt.Format(time.RFC3339))
	}
	if s.hasSolved() {
		add("solved_at", s.SolvedAt.Format(time.RFC3339))
	}
	if s.hasDuration() {
		add("duration_ms", strconv.FormatInt(s.DurationMs, 10))
	}
	if s.hasTarget() {
		add("target_ms", strconv.FormatInt(s.TargetMs, 10))
	}
	if s.AC != nil {
		add("ac", strconv.FormatBool(*s.AC))
	}
	if s.Editorial != nil {
		add("editorial", strconv.FormatBool(*s.Editorial))
	}
	if s.Score.Knowledge >= 0 {
		add("knowledge", strconv.Itoa(s.Score.Knowledge))
	}
	if s.Score.Translation >= 0 {
		add("translation", strconv.Itoa(s.Score.Translation))
	}
	if s.Score.Complexity >= 0 {
		add("complexity", strconv.Itoa(s.Score.Complexity))
	}
	if s.Score.Impl >= 0 {
		add("impl", strconv.Itoa(s.Score.Impl))
	}
	if s.Score.Verify >= 0 {
		add("verify", strconv.Itoa(s.Score.Verify))
	}
	b.WriteString(endMarker + "\n")
	return b.String()
}

func atomicWrite(path string, data []byte) error {
	dir := filepath.Dir(path)
	tmp, err := os.CreateTemp(dir, ".solvestat-*.tmp")
	if err != nil {
		return err
	}
	tmpName := tmp.Name()
	defer os.Remove(tmpName)
	if _, err := tmp.Write(data); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}
	// 既存ファイルのパーミッションを踏襲 (無ければ CreateTemp の既定)。
	if info, statErr := os.Stat(path); statErr == nil {
		_ = os.Chmod(tmpName, info.Mode())
	}
	return os.Rename(tmpName, path)
}
