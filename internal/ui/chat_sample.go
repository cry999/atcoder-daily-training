package ui

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/extracase"
)

// chat の :test (要件 045) が読むサンプルケースの場所解決・列挙ヘルパ。
// 公式サンプル (tests/) と追加ケース (tests-extra/、要件 024) を、バッチ test の
// collectCases と同じ表示 ID 規約 (公式 "01" / 追加 "x01") で扱う。internal/ui は
// fetch/judge (testexec) を知らない層境界を保つため、ここでは os/extracase だけに依存し
// キャッシュ済みファイルを読むだけにする (取得は atcoder test、追加保存は :w が担う)。

// normalizeCaseName は数値 (0..99) のケース名を %02d に揃える純粋関数。
// 数値でない名前 (任意名の追加ケース) はそのまま返す。バッチ test の同名関数と同規約。
func normalizeCaseName(s string) string {
	if n, err := strconv.Atoi(s); err == nil && n >= 0 && n < 100 {
		return fmt.Sprintf("%02d", n)
	}
	return s
}

// normalizeSampleRef は :test の引数 (表示 ID 風の参照) を (サブディレクトリ, ファイル名)
// に振り分ける純粋関数。先頭が x|X なら追加ケース (tests-extra)、それ以外は公式 (tests)。
// いずれも数字は %02d 正規化する ("1"→"01" / "x1"→tests-extra "01")。空参照は name="" を返す。
func normalizeSampleRef(ref string) (dir, name string) {
	ref = strings.TrimSpace(ref)
	if ref == "" {
		return "tests", ""
	}
	if ref[0] == 'x' || ref[0] == 'X' {
		return extracase.DirName, normalizeCaseName(ref[1:])
	}
	return "tests", normalizeCaseName(ref)
}

// listSampleCases は TaskDir 配下のキャッシュ済みケースの表示 ID を昇順 (公式→追加) で返す。
// 公式はファイル名のまま (例 "01")、追加は "x" プレフィックス付き (例 "x01")。
func listSampleCases(taskDir string) []string {
	var ids []string
	ids = append(ids, listInFiles(filepath.Join(taskDir, "tests"))...)
	extra, _ := extracase.List(taskDir) // best-effort: 失敗時は追加ケースなし扱い
	for _, n := range extra {
		ids = append(ids, "x"+n)
	}
	return ids
}

// listInFiles は dir 直下の *.in の basename (拡張子なし) を昇順で返す。
// dir が無ければ空 (サンプル未取得は正常)。
func listInFiles(dir string) []string {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil
	}
	var names []string
	for _, e := range entries {
		if e.IsDir() || !strings.HasSuffix(e.Name(), ".in") {
			continue
		}
		names = append(names, strings.TrimSuffix(e.Name(), ".in"))
	}
	sort.Strings(names)
	return names
}

// resolveSampleCase は ref を解決し、入力行 (.in)・期待行 (.out)・正規化した表示 ID を返す。
// .in が読めなければ ok=false。.out 欠落は空 expected として許容する (検証なしで流せる)。
func resolveSampleCase(taskDir, ref string) (in, out []string, id string, ok bool) {
	dir, name := normalizeSampleRef(ref)
	if name == "" {
		return nil, nil, "", false
	}
	base := filepath.Join(taskDir, dir)
	inBytes, err := os.ReadFile(filepath.Join(base, name+".in"))
	if err != nil {
		return nil, nil, "", false
	}
	outBytes, _ := os.ReadFile(filepath.Join(base, name+".out")) // 欠落は空 expected
	id = name
	if dir == extracase.DirName {
		id = "x" + name
	}
	return splitLines(string(inBytes)), splitLines(string(outBytes)), id, true
}
