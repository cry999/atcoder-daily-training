package testexec

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/gen"
)

// GenSourceFileName は入力生成の解析元 (生セクション) を置くキャッシュファイル名。
const GenSourceFileName = "gen.toml"

// genSourcePath は contest/task の gen.toml のパスを返す。
func genSourcePath(contest, task string) string {
	return filepath.Join(cachepath.Task(contest, task), GenSourceFileName)
}

// saveGenSource は fetch した problem の生セクションを gen.toml に書く
// (ベストエフォート。taskDir は存在している前提 = サンプル保存の後に呼ぶ)。
// 生セクションが両方空なら書かない (空ファイルでキャッシュを汚さない)。
func saveGenSource(taskDir string, prob *problem) {
	if prob == nil || (prob.InputFormat == "" && prob.Constraints == "") {
		return
	}
	raw := &gen.Raw{
		FetchedAt:   time.Now(),
		InputFormat: prob.InputFormat,
		Constraints: prob.Constraints,
	}
	_ = gen.Save(filepath.Join(taskDir, GenSourceFileName), raw)
}

// EnsureGenSource は contest/task の入力生成用生セクション (gen.toml) を用意して返す
// (要件 060)。キャッシュ済みで refresh でなければそれを読み、無ければ問題ページを
// fetch して gen.toml に保存する。サンプルキャッシュ (tests/ / meta.toml) は
// このパスでは touch しない (gen.toml の準備に専念)。
func EnsureGenSource(reporter Reporter, contest, task string, refresh bool) (*gen.Raw, error) {
	path := genSourcePath(contest, task)
	if !refresh {
		if raw, err := gen.Load(path); err == nil && raw.HasContent() {
			return raw, nil
		}
	}

	// 取得元 URL を決める (meta.toml の url override を尊重。既存 fetch と同じ流儀)。
	metaPath := metaPathFor(contest, task)
	override := ""
	if m, err := loadMeta(metaPath); err == nil {
		override = m.URL
	}
	url := resolveFetchURL(contest, task, override)

	if reporter != nil {
		reporter.Fetching(contest, task)
	}
	prob, err := fetchProblem(url)
	if err != nil {
		return nil, fmt.Errorf("AtCoder から取得できませんでした: %w", err)
	}
	if prob.InputFormat == "" && prob.Constraints == "" {
		return nil, fmt.Errorf("この問題では制約 / 入力形式の節が見つかりませんでした")
	}

	taskDir := cachepath.Task(contest, task)
	if err := os.MkdirAll(taskDir, 0o755); err != nil {
		return nil, err
	}
	raw := &gen.Raw{
		FetchedAt:   time.Now(),
		InputFormat: prob.InputFormat,
		Constraints: prob.Constraints,
	}
	if err := gen.Save(path, raw); err != nil {
		return nil, err
	}
	return raw, nil
}
