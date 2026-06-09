package main

import "flag"

// 共通フラグの定義を 1 か所にまとめる。test / run / submit が同じ --task / --layout
// を各自で `flags.String(...)` していたため、ヘルプ文やデフォルト値がドリフトし
// やすかった。登録ヘルパを共有して定義を一本化する (挙動は従来と同一)。

// addTaskFlag は共通の --task フラグを fs に登録し、値ポインタを返す。
func addTaskFlag(fs *flag.FlagSet) *string {
	return fs.String("task", "", `AtCoder task ID, or short form (e.g. "d" expands to "<contest>_d")`)
}

// addLayoutFlag は共通の --layout フラグを fs に登録し、値ポインタを返す。
func addLayoutFlag(fs *flag.FlagSet) *string {
	return fs.String("layout", "auto", "Solution file layout (auto, abc, exercise). auto picks abc for abc<NNN>, exercise otherwise.")
}
