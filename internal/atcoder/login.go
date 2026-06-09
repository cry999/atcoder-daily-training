package atcoder

// AtCoder への HTTP アクセスで共通に使う定数。
//
// 注: かつては username / password での programmatic ログインをここに実装していたが、
// AtCoder のログインページが Cloudflare Turnstile (ボット対策) を導入したため、
// ブラウザの JS が生成する検証トークン無しでは認証できなくなった。ログインは
// ブラウザの REVEL_SESSION cookie を取り込む方式 (cookie.go / cmd/atcoder/login.go)
// に置き換えた。
const (
	baseURL   = "https://atcoder.jp"
	userAgent = "atcoder-status/0.1 (+https://github.com/cry999/atcoder-daily-training)"
)
