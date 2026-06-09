// Package selfupdate は atcoder 自身のバージョン取得・最新解決・再インストールを担う。
//
// 現在版は Go が実行ファイルに自動で埋め込む VCS 情報 (runtime/debug.ReadBuildInfo)
// から読む。最新版の解決と再インストールは go ツールチェインに委譲する
// (go list -m / go install ...@latest)。git タグ運用や -ldflags は使わない。
// AtCoder には一切アクセスしない (触る外部は go module proxy / GitHub だけ)。
//
// 要件詳細: docs/tools/requirements/013-atcoder-self-update.md
package selfupdate

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime/debug"
	"strings"
	"time"
)

// DefaultModule は VCS 情報からモジュールパスが取れないときのフォールバック。
const DefaultModule = "github.com/cry999/atcoder-daily-training"

// cmdSubpath は go install するメインパッケージのサブパス。
const cmdSubpath = "/cmd/atcoder"

// Current はビルド時に埋め込まれた VCS 情報から読む現在版。Known=false なら不明。
type Current struct {
	Module   string    // モジュールパス (bi.Main.Path)
	Revision string    // vcs.revision (フル sha)。Known=false なら空
	Time     time.Time // vcs.time (コミット日時)
	Modified bool      // vcs.modified (dirty ビルドか)
	Known    bool
}

// ReadCurrent は runtime/debug.ReadBuildInfo から現在版を組み立てる。
func ReadCurrent() Current {
	bi, ok := debug.ReadBuildInfo()
	if !ok {
		return Current{Module: DefaultModule}
	}
	return currentFromBuildInfo(bi)
}

// currentFromBuildInfo は BuildInfo から現在版を取り出す (ReadCurrent の中身、
// テスト用に分離)。
//
// 版の出所は 2 通り:
//   - `go install ./cmd/atcoder` など作業ツリーからのビルド → vcs.* スタンプ
//     (revision はフル sha、time/modified も付く)。
//   - `go install <module>@latest` (= atcoder update) → 作業ツリーではなく
//     ダウンロード済みモジュールからのビルドなので vcs.* は付かず、代わりに
//     Main.Version が pseudo-version になる。ここから sha と日時を補う。
func currentFromBuildInfo(bi *debug.BuildInfo) Current {
	c := Current{Module: bi.Main.Path}
	if c.Module == "" {
		c.Module = DefaultModule
	}
	for _, s := range bi.Settings {
		switch s.Key {
		case "vcs.revision":
			c.Revision = s.Value
		case "vcs.time":
			if t, err := time.Parse(time.RFC3339, s.Value); err == nil {
				c.Time = t
			}
		case "vcs.modified":
			c.Modified = s.Value == "true"
		}
	}
	// VCS スタンプが無い (update でインストールされた) 場合は pseudo-version で補う。
	if c.Revision == "" {
		if sha := pseudoSha(bi.Main.Version); sha != "" {
			c.Revision = sha
			if t, ok := pseudoTime(bi.Main.Version); ok {
				c.Time = t
			}
		}
	}
	c.Known = c.Revision != ""
	return c
}

// ShortRev は revision の先頭 12 文字を返す (revision が無ければ "unknown")。
func (c Current) ShortRev() string {
	if c.Revision == "" {
		return "unknown"
	}
	return shortSha(c.Revision)
}

// Latest は go module proxy が返す最新版。
type Latest struct {
	Version string    // pseudo-version またはタグ (例 v0.0.0-2026...-44f73cc537c7)
	Sha     string    // pseudo-version 末尾の短縮 sha。タグ版なら空
	Time    time.Time // コミット日時
}

// goListModule は `go list -m -json` の必要フィールドだけ。
type goListModule struct {
	Version string
	Time    time.Time
}

// ResolveLatest は中立 dir で `go list -m -json <module>@latest` を実行し最新版を読む。
// module が空なら DefaultModule。go 不在・network/proxy 失敗・パース失敗は error。
func ResolveLatest(ctx context.Context, module string) (Latest, error) {
	if module == "" {
		module = DefaultModule
	}
	dir, err := neutralDir()
	if err != nil {
		return Latest{}, err
	}
	defer os.RemoveAll(dir)

	cmd := exec.CommandContext(ctx, "go", "list", "-m", "-json", module+"@latest")
	cmd.Dir = dir
	cmd.Env = goEnv(module)
	var stdout, stderr strings.Builder
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		msg := strings.TrimSpace(stderr.String())
		if msg == "" {
			msg = err.Error()
		}
		return Latest{}, fmt.Errorf("resolve latest version: %s", msg)
	}
	var m goListModule
	if err := json.Unmarshal([]byte(stdout.String()), &m); err != nil {
		return Latest{}, fmt.Errorf("parse `go list` output: %w", err)
	}
	return Latest{Version: m.Version, Sha: pseudoSha(m.Version), Time: m.Time}, nil
}

// Available は cur と latest から更新の要否を返す。
// 現在版が不明 / dirty ビルドのときは正確に比較できないため「更新あり」(true) とする。
func Available(cur Current, latest Latest) bool {
	if !cur.Known || cur.Modified {
		return true
	}
	if latest.Sha != "" && strings.HasPrefix(cur.Revision, latest.Sha) {
		return false // 同一コミット
	}
	if !latest.Time.IsZero() && !cur.Time.IsZero() {
		return latest.Time.After(cur.Time)
	}
	// 時刻で比較できず sha も一致しない → 別版とみなす。
	return true
}

// Install は `go install <module>/cmd/atcoder@latest` を中立 dir で実行し、
// go の出力を out にストリームする。go 不在・install 失敗は error。
func Install(ctx context.Context, module string, out io.Writer) error {
	if module == "" {
		module = DefaultModule
	}
	dir, err := neutralDir()
	if err != nil {
		return err
	}
	defer os.RemoveAll(dir)

	cmd := exec.CommandContext(ctx, "go", "install", module+cmdSubpath+"@latest")
	cmd.Dir = dir
	cmd.Env = goEnv(module)
	cmd.Stdout = out
	cmd.Stderr = out
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("go install %s%s@latest: %w", module, cmdSubpath, err)
	}
	return nil
}

// InstallLocal は cwd の作業ツリーから `go install ./cmd/atcoder` を実行する
// (= atcoder update --local)。proxy も最新解決も伴わず、いま手元にあるソースを
// そのままインストールするので、未 push のローカルコミットも反映できる。
//
// 中立 dir は使わない: 相対パス ./cmd/atcoder を解決するため、呼び出し時の cwd
// (= リポジトリ内である前提) で実行する。cwd がモジュール外なら go がエラーを返す。
func InstallLocal(ctx context.Context, out io.Writer) error {
	cmd := exec.CommandContext(ctx, "go", "install", "./cmd/atcoder")
	cmd.Env = os.Environ()
	cmd.Stdout = out
	cmd.Stderr = out
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("go install ./cmd/atcoder: %w", err)
	}
	return nil
}

// goEnv は os.Environ() に、自モジュールを GOPRIVATE に含めた環境を返す。
//
// proxy.golang.org は @latest を一定時間キャッシュするため、push 直後は古い
// コミットを返すことがある (実際に「最新のはずが古い main tip がインストール
// される」不具合の原因になった)。GOPRIVATE に自モジュールを入れると、go は
// proxy を介さず git remote へ直接問い合わせ、常に origin デフォルトブランチの
// 現在 HEAD を解決する。あわせて sumdb 検証もこのモジュールについてはスキップ
// される (自分のリポジトリなので可)。依存モジュールは GOPRIVATE に含めないので
// 通常どおり proxy + sumdb 経由のまま。既存の GOPRIVATE は保全して追記する。
func goEnv(module string) []string {
	env := os.Environ()
	const key = "GOPRIVATE="
	for i, kv := range env {
		if !strings.HasPrefix(kv, key) {
			continue
		}
		existing := strings.TrimPrefix(kv, key)
		switch {
		case existing == "":
			env[i] = key + module
		case !privateContains(existing, module):
			env[i] = key + existing + "," + module
		}
		return env
	}
	return append(env, key+module)
}

// privateContains は GOPRIVATE のカンマ区切りリストに module が既に含まれるか。
func privateContains(list, module string) bool {
	for _, p := range strings.Split(list, ",") {
		if p == module {
			return true
		}
	}
	return false
}

// neutralDir はどのモジュールにも属さない一時 dir を作る。`go list -m @latest` は
// module 文脈 (go.mod) を要するので、最小の go.mod を置いておく。呼び出し側が
// os.RemoveAll で後始末する。リポジトリ内で実行されても module 文脈に干渉しない。
func neutralDir() (string, error) {
	dir, err := os.MkdirTemp("", "atcoder-selfupdate-")
	if err != nil {
		return "", err
	}
	gomod := "module atcoder-selfupdate-query\n\ngo 1.21\n"
	if err := os.WriteFile(filepath.Join(dir, "go.mod"), []byte(gomod), 0o644); err != nil {
		os.RemoveAll(dir)
		return "", err
	}
	return dir, nil
}

// shortSha は sha の先頭 12 文字 (短いものはそのまま)。
func shortSha(s string) string {
	if len(s) > 12 {
		return s[:12]
	}
	return s
}

// hex12RE は pseudo-version 末尾の 12 桁 16 進 sha。
var hex12RE = regexp.MustCompile(`^[0-9a-f]{12}$`)

// pseudoSha は pseudo-version 末尾の短縮 sha を取り出す。タグ版など末尾が
// 12 桁 16 進でなければ空文字を返す。
//
//	"v0.0.0-20260609084444-44f73cc537c7" → "44f73cc537c7"
//	"v1.2.3"                             → ""
func pseudoSha(version string) string {
	i := strings.LastIndex(version, "-")
	if i < 0 || i+1 >= len(version) {
		return ""
	}
	if tail := version[i+1:]; hex12RE.MatchString(tail) {
		return tail
	}
	return ""
}

// pseudoTime は pseudo-version 中の 14 桁タイムスタンプ (yyyymmddhhmmss, UTC) を
// 取り出す。形式が合わなければ ok=false。
//
//	"v0.0.0-20260609101134-4c7e3b9c0d74" → 2026-06-09T10:11:34Z
func pseudoTime(version string) (time.Time, bool) {
	parts := strings.Split(version, "-")
	if len(parts) < 3 {
		return time.Time{}, false
	}
	t, err := time.Parse("20060102150405", parts[len(parts)-2])
	if err != nil {
		return time.Time{}, false
	}
	return t.UTC(), true
}
