package testexec

import (
	"os"
	"path/filepath"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/cry999/atcoder-daily-training/internal/cachepath"
)

// Meta はキャッシュした meta.toml の内容。`atcoder meta` (要件 046) が表示・編集の
// ために参照するため公開している。
type Meta struct {
	Contest     string    `toml:"contest"`
	Task        string    `toml:"task"`
	URL         string    `toml:"url"`
	TimeLimitMs int       `toml:"time_limit_ms"`
	FetchedAt   time.Time `toml:"fetched_at"`
}

func loadMeta(path string) (*Meta, error) {
	var m Meta
	if _, err := toml.DecodeFile(path, &m); err != nil {
		return nil, err
	}
	return &m, nil
}

func saveMeta(path string, m *Meta) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	return toml.NewEncoder(f).Encode(m)
}

// metaPathFor は contest/task のキャッシュ済み meta.toml のパスを返す。
func metaPathFor(contest, task string) string {
	return filepath.Join(cachepath.Task(contest, task), "meta.toml")
}

// LoadMeta は contest/task のキャッシュ済み meta.toml を読む。未取得 (ファイル無し)
// なら error。`atcoder meta show/set` 用の公開ラッパー。
func LoadMeta(contest, task string) (*Meta, error) {
	return loadMeta(metaPathFor(contest, task))
}

// SaveMeta は contest/task の meta.toml を書き戻す。キャッシュディレクトリが無ければ
// 作成する。`atcoder meta set` 用の公開ラッパー。
func SaveMeta(contest, task string, m *Meta) error {
	taskDir := cachepath.Task(contest, task)
	if err := os.MkdirAll(taskDir, 0o755); err != nil {
		return err
	}
	return saveMeta(filepath.Join(taskDir, "meta.toml"), m)
}

// SampleCount は contest/task の tests/ にあるサンプルケース数を返す。
func SampleCount(contest, task string) (int, error) {
	testsDir := filepath.Join(cachepath.Task(contest, task), "tests")
	names, err := listCases(testsDir)
	if err != nil {
		return 0, err
	}
	return len(names), nil
}
