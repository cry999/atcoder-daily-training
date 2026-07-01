package ui

import (
	"bytes"
	"encoding/json"
	"strings"
)

// debugLinePrefix は [DEBUG] 行の識別子。testexec.DebugPrefix と同値だが、pp は
// 表示層 (internal/ui) に閉じる純粋なレンダリング処理なので、層境界を跨いで
// testexec を import しないようローカル定数を持つ (chat.go の debugPrefix と一貫)。
const debugLinePrefix = "[DEBUG]"

// prettifyDebug は debug (複数行の [DEBUG] 行集合) を走査し、各行のペイロードが
// 単独で valid JSON ({ or [ 始まり) のものだけを 2-space インデントに整形して返す。
// 整形対象外の行・空文字列はそのまま返す純関数。verdict・保存値・--json は変えない。
//
//	入力:  "[DEBUG] {\"n\":5}\n[DEBUG] dp = {...}"
//	出力:  "[DEBUG] {\n  \"n\": 5\n}\n[DEBUG] dp = {...}"  // 2 行目は非 JSON なので素通し
func prettifyDebug(debug string) string {
	if debug == "" {
		return debug
	}
	lines := strings.Split(debug, "\n")
	for i, line := range lines {
		if !strings.HasPrefix(line, debugLinePrefix) {
			continue // [DEBUG] 行でなければそのまま
		}
		payload := strings.TrimSpace(strings.TrimPrefix(line, debugLinePrefix))
		if pretty, ok := prettifyJSONPayload(payload); ok {
			lines[i] = debugLinePrefix + " " + pretty
		}
	}
	return strings.Join(lines, "\n")
}

// prettifyJSONPayload は payload が { or [ 始まりの valid JSON なら 2-space
// インデントに整形して (result, true) を返す。そうでなければ ("", false)。
// json.Indent を使う (Unmarshal+Marshal しない) ため、キー順・数値表記は保存される。
func prettifyJSONPayload(payload string) (string, bool) {
	if payload == "" {
		return "", false
	}
	if payload[0] != '{' && payload[0] != '[' {
		return "", false // スカラ / ラベル付きは対象外 (要件 047 の設計境界)
	}
	if !json.Valid([]byte(payload)) {
		return "", false // ペイロード全体が valid JSON のときだけ整形する
	}
	var buf bytes.Buffer
	if err := json.Indent(&buf, []byte(payload), "", "  "); err != nil {
		return "", false // json.Valid 通過後は理論上起きないが、失敗時は素通し
	}
	return buf.String(), true
}
