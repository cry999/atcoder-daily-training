package main

import (
	"flag"
	"os"

	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/mode"
)

// 共通フラグの定義を 1 か所にまとめる。test / start / record が同じ --task / --mode
// を各自で `flags.String(...)` すると、ヘルプ文やデフォルト値がドリフトし
// やすい。登録ヘルパを共有して定義を一本化する。

// modeEnvVar は既定 mode を上書きする環境変数名。config より優先される。
const modeEnvVar = "ATCODER_MODE"

// addTaskFlag は共通の --task フラグを fs に登録し、値ポインタを返す。
func addTaskFlag(fs *flag.FlagSet) *string {
	return fs.String("task", "", `AtCoder task ID, or short form (e.g. "d" expands to "<contest>_d")`)
}

// addModeFlag は共通の --mode フラグを fs に登録し、値ポインタを返す。
// デフォルトは空 ("") = 未指定で、env (ATCODER_MODE) → config → exercise に
// フォールバックする (resolveMode が解決)。明示すればそれが最優先。
func addModeFlag(fs *flag.FlagSet) *string {
	return fs.String("mode", "", "Solution file mode (contest, exercise). Empty = use $ATCODER_MODE / config / exercise.")
}

// resolveMode は test/start/record が使う共通ヘルパー。コマンドの --mode フラグ
// (未指定は "") に、環境変数と config.toml を組み合わせて Mode を解決する。
// precedence は flag > env > config > exercise (mode.Resolve に集約)。config は
// 読むだけで書かない。不正な値はエラー (呼び出し側が exit 2 にする)。
func resolveMode(flagValue string) (mode.Mode, error) {
	cfg, err := config.Load()
	if err != nil {
		return nil, err
	}
	m, _, _, err := mode.Resolve(flagValue, os.Getenv(modeEnvVar), cfg.Mode)
	return m, err
}
