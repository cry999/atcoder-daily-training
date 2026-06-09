package main

import (
	"flag"
	"os"

	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/layout"
)

// 共通フラグの定義を 1 か所にまとめる。test / run / submit が同じ --task / --layout
// を各自で `flags.String(...)` していたため、ヘルプ文やデフォルト値がドリフトし
// やすかった。登録ヘルパを共有して定義を一本化する (挙動は従来と同一)。

// layoutEnvVar は既定レイアウトを上書きする環境変数名。config より優先される。
const layoutEnvVar = "ATCODER_LAYOUT"

// addTaskFlag は共通の --task フラグを fs に登録し、値ポインタを返す。
func addTaskFlag(fs *flag.FlagSet) *string {
	return fs.String("task", "", `AtCoder task ID, or short form (e.g. "d" expands to "<contest>_d")`)
}

// addLayoutFlag は共通の --layout フラグを fs に登録し、値ポインタを返す。
// デフォルトは空 ("") = 未指定で、env (ATCODER_LAYOUT) → config → auto に
// フォールバックする (resolveLayout が解決)。明示すればそれが最優先。
func addLayoutFlag(fs *flag.FlagSet) *string {
	return fs.String("layout", "", "Solution file layout (auto, abc, exercise). Empty = use $ATCODER_LAYOUT / config / auto. auto picks abc for abc<NNN>, exercise otherwise.")
}

// resolveLayout は test/run/submit が使う共通ヘルパー。コマンドの --layout フラグ
// (未指定は "") に、環境変数と config.toml を組み合わせて Layout を解決する。
// precedence は flag > env > config > auto (layout.Resolve に集約)。config は
// 読むだけで書かない。不正な値はエラー (呼び出し側が exit 2 にする)。
func resolveLayout(flagValue, contest string) (layout.Layout, error) {
	cfg, err := config.Load()
	if err != nil {
		return nil, err
	}
	lay, _, _, err := layout.Resolve(flagValue, os.Getenv(layoutEnvVar), cfg.Layout, contest)
	return lay, err
}
