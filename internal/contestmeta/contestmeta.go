// Package contestmeta はコンテスト単位のメタ情報 (タスクリスト・開始 / 終了時刻・
// タイトル・URL) を扱う。タスク単位の meta.toml (internal/testexec) と対になる層で、
// `$XDG_CACHE_HOME/atcoder-tools/<contest>/contest.toml` に保存する。
//
// 主な利用者は `atcoder new abc <contest>` の一括準備で、保存したメタは将来の
// 本番モード判定 (E) やタイマー (G) の入力になる。
package contestmeta

import (
	"os"
	"path/filepath"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/cry999/atcoder-daily-training/internal/cachepath"
)

// Meta は contest.toml のスキーマ。
type Meta struct {
	Contest    string    `toml:"contest"`
	URL        string    `toml:"url"`
	Title      string    `toml:"title"`
	StartAt    time.Time `toml:"start_at"`
	EndAt      time.Time `toml:"end_at"`
	DurationMs int       `toml:"duration_ms"`
	Tasks      []string  `toml:"tasks"`
	FetchedAt  time.Time `toml:"fetched_at"`
}

// Path は指定 contest の contest.toml の保存パスを返す。
func Path(contest string) string {
	return filepath.Join(cachepath.Contest(contest), "contest.toml")
}

// Load は contest.toml を読み込む。
func Load(path string) (*Meta, error) {
	var m Meta
	if _, err := toml.DecodeFile(path, &m); err != nil {
		return nil, err
	}
	return &m, nil
}

// Save は contest.toml を書き出す (親ディレクトリは必要なら作成する)。
func Save(path string, m *Meta) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	return toml.NewEncoder(f).Encode(m)
}
