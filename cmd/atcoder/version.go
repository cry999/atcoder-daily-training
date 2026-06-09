package main

import (
	"fmt"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/selfupdate"
)

// cmdVersion は現在インストールされている atcoder の版 (ビルド時に埋め込まれた
// VCS 情報) を表示する。オフラインで動き、副作用は無い。常に exit 0。
func cmdVersion(args []string) (int, error) {
	fmt.Println("atcoder " + describeCurrent(selfupdate.ReadCurrent()))
	return 0, nil
}

// describeCurrent は現在版を "<short-sha> (<time>)[ dirty]" 形式の文字列にする。
// version / update の両方が使う。
func describeCurrent(cur selfupdate.Current) string {
	if !cur.Known {
		return "unknown (no VCS build info)"
	}
	s := cur.ShortRev()
	if !cur.Time.IsZero() {
		s += " (" + cur.Time.Format(time.RFC3339) + ")"
	}
	if cur.Modified {
		s += " dirty"
	}
	return s
}
