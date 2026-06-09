// Package cachepath は `atcoder` 系コマンドが保持するキャッシュ
// (meta.toml, tests/NN.in NN.out 等) の配置場所を解決する。
//
// XDG Base Directory Specification (https://specifications.freedesktop.org/basedir-spec/)
// に従い、以下の優先順で base directory を決める:
//
//  1. 環境変数 $XDG_CACHE_HOME (絶対パスを期待)
//  2. ~/.cache (ホームディレクトリが分かるとき)
//  3. ./.cache (最終 fallback。普通到達しない)
//
// 最終的な配置:
//
//	<base>/atcoder-tools/<contest>/<task>/
//	  meta.toml
//	  tests/
//	    01.in
//	    01.out
//	    ...
package cachepath

import (
	"os"
	"path/filepath"
)

// AppName はキャッシュ階層における本リポジトリ全体の名前。複数の `atcoder`
// クローン (自宅 / 職場 等) や、将来この階層を共有する別ツールから見ても識別
// しやすい中立な名前にしている。
const AppName = "atcoder-tools"

// Contest は指定された contest のキャッシュディレクトリを返す。
// contest.toml (コンテストメタ) とタスク単位のサブディレクトリがこの下に並ぶ。
// パスは存在するとは限らない (呼び出し側が必要に応じて MkdirAll する)。
func Contest(contest string) string {
	return filepath.Join(Base(), AppName, contest)
}

// Task は指定された contest / task のキャッシュディレクトリを返す。
// パスは存在するとは限らない (呼び出し側が必要に応じて MkdirAll する)。
func Task(contest, task string) string {
	return filepath.Join(Contest(contest), task)
}

// Base は XDG_CACHE_HOME (or fallback) のディレクトリを返す。
func Base() string {
	if v := os.Getenv("XDG_CACHE_HOME"); v != "" {
		return v
	}
	if home, err := os.UserHomeDir(); err == nil {
		return filepath.Join(home, ".cache")
	}
	return ".cache"
}
