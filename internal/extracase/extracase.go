// Package extracase は contest/task のユーザ追加ケース (tests-extra/) の
// 場所解決・保存・列挙を担う。--refresh で消える公式サンプル (tests/) とは
// 別系統として扱い、--refresh の取得・削除の対象に含めない。
//
// 追加ケースはインタラクティブ chat のケースビルダー (要件 024) で作られ、
// atcoder test / start の判定ループで公式サンプルの後ろに連結して走る。
package extracase

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
)

// DirName は taskDir 直下に置くユーザ追加ケース用ディレクトリ名。
const DirName = "tests-extra"

// Dir は taskDir (cache 配下の <contest>/<task>) に対する tests-extra のパスを返す。
func Dir(taskDir string) string {
	return filepath.Join(taskDir, DirName)
}

// List は tests-extra のケース名 (拡張子なしの basename、例 "01") を昇順で返す。
// ディレクトリが無ければ空スライスと nil を返す (追加ケースが無いのは正常)。
func List(taskDir string) ([]string, error) {
	dir := Dir(taskDir)
	entries, err := os.ReadDir(dir)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, nil
		}
		return nil, err
	}
	var names []string
	for _, e := range entries {
		if e.IsDir() || !strings.HasSuffix(e.Name(), ".in") {
			continue
		}
		names = append(names, strings.TrimSuffix(e.Name(), ".in"))
	}
	sort.Strings(names)
	return names, nil
}

// Save は input/expected を tests-extra/<name>.in|.out に書き出し、付与した名前を返す。
// name が空なら既存の最大番号 + 1 を %02d で採番する。既存 name への上書きは
// error (冪等性のため: :w は常に新規追加で、誤上書きを防ぐ)。
func Save(taskDir, name string, input, expected []byte) (string, error) {
	dir := Dir(taskDir)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", err
	}
	if name == "" {
		n, err := nextSeq(dir)
		if err != nil {
			return "", err
		}
		name = fmt.Sprintf("%02d", n)
	}
	inPath := filepath.Join(dir, name+".in")
	outPath := filepath.Join(dir, name+".out")
	if _, err := os.Stat(inPath); err == nil {
		return "", fmt.Errorf("追加ケース %q は既に存在します (上書きしません)", name)
	}
	if err := os.WriteFile(inPath, input, 0o644); err != nil {
		return "", err
	}
	if err := os.WriteFile(outPath, expected, 0o644); err != nil {
		// .in だけ残らないよう後始末する。
		os.Remove(inPath)
		return "", err
	}
	return name, nil
}

// nextSeq は tests-extra 内の数値ケース名の最大 + 1 を返す (空なら 1)。
// 数値でない名前 (任意名で保存されたもの) は採番に影響しない。
func nextSeq(dir string) (int, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		if os.IsNotExist(err) {
			return 1, nil
		}
		return 0, err
	}
	max := 0
	for _, e := range entries {
		if e.IsDir() || !strings.HasSuffix(e.Name(), ".in") {
			continue
		}
		base := strings.TrimSuffix(e.Name(), ".in")
		if n, err := strconv.Atoi(base); err == nil && n > max {
			max = n
		}
	}
	return max + 1, nil
}
