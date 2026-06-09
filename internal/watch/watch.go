// Package watch は単一ファイルの変更検知を提供する。
//
// 検知は mtime のポーリング (定期 os.Stat) で行う。単一ファイル監視には十分で、
// fsnotify 等の外部依存・プラットフォーム差を持ち込まずに済む。エディタの
// atomic save (一旦削除/リネームしてから書き直す) でも、ファイル再出現時の
// mtime 変化として拾える。
package watch

import (
	"context"
	"os"
	"time"
)

// Watcher は 1 ファイルの mtime をポーリングして変更を検知する。
type Watcher struct {
	path     string
	interval time.Duration
	debounce time.Duration
	last     time.Time // 直近に観測した mtime (基準)
}

// New は path を監視する Watcher を作る。基準 mtime は生成時点の値
// (ファイルが無ければゼロ値)。interval はポーリング間隔、debounce は変更検知後に
// 連続書き込みを 1 回にまとめるための待機。
func New(path string, interval, debounce time.Duration) *Watcher {
	return &Watcher{
		path:     path,
		interval: interval,
		debounce: debounce,
		last:     mtime(path),
	}
}

// WaitForChange は監視ファイルの mtime が基準から変わるまでブロックする。
// 変化を検知したら debounce 待機後に基準を更新して true を返す。
// ctx が先に done なら false を返す (Ctrl+C / 終了)。
func (w *Watcher) WaitForChange(ctx context.Context) bool {
	ticker := time.NewTicker(w.interval)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return false
		case <-ticker.C:
			cur := mtime(w.path)
			if cur.Equal(w.last) {
				continue
			}
			// 連続書き込み (エディタの複数回 write) を 1 回にまとめる。
			// debounce 中の中断にも応じる。
			if w.debounce > 0 {
				select {
				case <-ctx.Done():
					return false
				case <-time.After(w.debounce):
				}
			}
			// debounce 後の最終 mtime を基準にする (待機中の追加書き込みも吸収)。
			w.last = mtime(w.path)
			return true
		}
	}
}

// mtime は path の最終更新時刻を返す。stat 失敗 (ファイル無し等) はゼロ値。
// ファイルの出現・消滅もゼロ値との差として mtime 変化に乗る。
func mtime(path string) time.Time {
	fi, err := os.Stat(path)
	if err != nil {
		return time.Time{}
	}
	return fi.ModTime()
}
