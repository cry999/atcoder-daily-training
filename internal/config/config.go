// Package config は `exercise` のユーザ設定ファイル (config.toml) を解決・読み込む。
//
// キャッシュ (internal/cachepath, XDG_CACHE_HOME) と対をなす「個人の既定値」の層。
// XDG Base Directory Specification に従い、設定は XDG_CONFIG_HOME 配下に置く:
//
//  1. 環境変数 $XDG_CONFIG_HOME
//  2. ~/.config (ホームディレクトリが分かるとき)
//  3. ./.config (最終 fallback。普通到達しない)
//
// 最終的な配置:
//
//	<base>/atcoder-daily-training/config.toml
//
// 優先順位は flag > config > default。各サブコマンドは flag のデフォルト値に
// config 値を流し込むことで、明示フラグ > config > 組み込み既定値 を実現する。
package config

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/BurntSushi/toml"
)

// AppName は設定階層における本リポジトリの名前。キャッシュ側の中立名
// (atcoder-tools) とは別で、こちらは「このツール個人設定」であることを示す。
const AppName = "atcoder-daily-training"

// FileName は設定ファイル名。
const FileName = "config.toml"

// Config は config.toml のスキーマ。サブコマンドごとにセクションを切る。
// 未知のキー/セクションは toml デコード時に無視され、前方/後方互換を保つ。
type Config struct {
	Test TestConfig `toml:"test"`
}

// TestConfig は [test] セクション。exercise test の既定値。
type TestConfig struct {
	// SideBySide は FAIL 時の diff を side-by-side でレンダリングする既定値 (-s 相当)。
	SideBySide bool `toml:"side_by_side"`
}

// Base は設定の base directory ($XDG_CONFIG_HOME or fallback) を返す。
func Base() string {
	if v := os.Getenv("XDG_CONFIG_HOME"); v != "" {
		return v
	}
	if home, err := os.UserHomeDir(); err == nil {
		return filepath.Join(home, ".config")
	}
	return ".config"
}

// Path は config.toml の絶対パスを返す。存在するとは限らない。
func Path() string {
	return filepath.Join(Base(), AppName, FileName)
}

// Load は config.toml を読む。ファイルが無いのは正常で、ゼロ値 Config と nil を
// 返す (全項目デフォルト)。パースに失敗したときだけ error を返す。
func Load() (*Config, error) {
	path := Path()
	var cfg Config
	if _, err := toml.DecodeFile(path, &cfg); err != nil {
		if os.IsNotExist(err) {
			return &cfg, nil
		}
		return nil, fmt.Errorf("設定ファイルの読み込みに失敗: %s: %w", path, err)
	}
	return &cfg, nil
}
