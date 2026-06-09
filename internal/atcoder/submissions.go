package atcoder

import (
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/antchfx/htmlquery"
	"golang.org/x/net/html"
)

// Submission は提出 1 件分。Source 実装間で共通の形にする。
type Submission struct {
	ID          int       // 提出 ID (個別ページ URL 末尾)
	Task        string    // task screen name 例 "abc258_d"
	TaskTitle   string    // 例 "D - Trophy"
	Verdict     string    // "AC" / "WA" / "WJ" / "Judging" など生の結果文字列
	Language    string    // 例 "Python (PyPy 3.11-v7.3.20)"
	ExecTimeMs  int       // 未確定時は 0
	MemoryKiB   int       // 未確定時は 0
	SubmittedAt time.Time // パースできなければゼロ値
	URL         string    // 個別提出ページ
}

// Source は提出一覧の取得元。認証あり (/submissions/me) を当面実装し、将来
// no-auth (kenkoooo) を別実装で足せるようにする前方互換の seam。
type Source interface {
	// Submissions は呼び出し元ユーザの contest 内提出を新しい順で返す。
	Submissions(contest string) ([]Submission, error)
}

// ErrSessionExpired はセッション cookie が失効していた (ログインページへ
// リダイレクトされた) ことを表す。
var ErrSessionExpired = fmt.Errorf("session expired")

// authedSource は認証付き client で /submissions/me を引く Source。
type authedSource struct {
	session *Session
}

// AuthedSource は cookie を載せた Source を返す。
func AuthedSource(s *Session) Source { return &authedSource{session: s} }

func (a *authedSource) Submissions(contest string) ([]Submission, error) {
	url := fmt.Sprintf("%s/contests/%s/submissions/me", baseURL, contest)
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", userAgent)
	req.Header.Set("Cookie", a.session.SessionCookie)

	// リダイレクトを追わず、/login への 302 = 失効として扱う。
	client := &http.Client{
		Timeout: 20 * time.Second,
		CheckRedirect: func(*http.Request, []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("提出一覧の取得に失敗: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusFound || resp.StatusCode == http.StatusMovedPermanently {
		return nil, ErrSessionExpired
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("提出一覧の取得に失敗: HTTP %d", resp.StatusCode)
	}

	doc, err := htmlquery.Parse(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("提出一覧の解析に失敗: %w", err)
	}
	return parseSubmissions(doc, contest), nil
}

var (
	subIDRe   = regexp.MustCompile(`/submissions/(\d+)`)
	taskIDRe  = regexp.MustCompile(`/tasks/([0-9a-z_]+)`)
	execTeRe  = regexp.MustCompile(`(\d+)\s*ms`)
	memoryRe  = regexp.MustCompile(`(\d+)\s*(KiB|KB)`)
	progressRe = regexp.MustCompile(`^\d+/\d+$`)
)

// parseSubmissions は /submissions/me のテーブルから各行を抽出する。
// 列順に依存せず、ID/task/verdict は href やラベル span から意味的に拾うことで、
// ジャッジ中 (実行時間・メモリ列が欠ける) でも壊れないようにする。
func parseSubmissions(doc *html.Node, contest string) []Submission {
	rows := htmlquery.Find(doc, `//table//tbody/tr`)
	var subs []Submission
	for _, row := range rows {
		s := parseRow(row, contest)
		if s.ID == 0 {
			continue // 提出行でなければスキップ
		}
		subs = append(subs, s)
	}
	return subs
}

func parseRow(row *html.Node, contest string) Submission {
	var s Submission

	// ID: 個別提出ページへのリンクから。
	for _, a := range htmlquery.Find(row, `.//a`) {
		href := htmlquery.SelectAttr(a, "href")
		if m := subIDRe.FindStringSubmatch(href); m != nil {
			if id, err := strconv.Atoi(m[1]); err == nil {
				s.ID = id
				s.URL = baseURL + "/contests/" + contest + "/submissions/" + m[1]
			}
		}
		if m := taskIDRe.FindStringSubmatch(href); m != nil && s.Task == "" {
			s.Task = m[1]
			s.TaskTitle = strings.TrimSpace(htmlquery.InnerText(a))
		}
	}

	// verdict: ラベル span のテキスト。ジャッジ中の "n/m" 進捗があれば添える。
	for _, sp := range htmlquery.Find(row, `.//span[contains(@class,"label")]`) {
		t := strings.TrimSpace(htmlquery.InnerText(sp))
		if t == "" {
			continue
		}
		if progressRe.MatchString(t) {
			// 進捗 (例 3/21) は verdict 本体に添える。
			if s.Verdict != "" {
				s.Verdict += " " + t
			}
			continue
		}
		if s.Verdict == "" {
			s.Verdict = t
		}
	}

	// 提出日時。
	if tnode := htmlquery.FindOne(row, `.//time`); tnode != nil {
		s.SubmittedAt = parseTime(strings.TrimSpace(htmlquery.InnerText(tnode)))
	}

	// 実行時間・メモリ・言語はセルのテキストから best-effort で拾う。
	tds := htmlquery.Find(row, `./td`)
	for _, td := range tds {
		txt := strings.TrimSpace(htmlquery.InnerText(td))
		if s.ExecTimeMs == 0 {
			if m := execTeRe.FindStringSubmatch(txt); m != nil {
				s.ExecTimeMs, _ = strconv.Atoi(m[1])
			}
		}
		if s.MemoryKiB == 0 {
			if m := memoryRe.FindStringSubmatch(txt); m != nil {
				s.MemoryKiB, _ = strconv.Atoi(m[1])
			}
		}
	}
	s.Language = guessLanguage(tds)
	return s
}

// guessLanguage は提出言語セルを推定する。言語列はリンク・時刻・結果ラベルを
// 含まず、数値や ms/KiB でもないセル。確実でなくても表示の補助なので
// best-effort (言語がリンク化されている場合は空を返す)。
func guessLanguage(tds []*html.Node) string {
	for _, td := range tds {
		if htmlquery.FindOne(td, `.//a`) != nil {
			continue // task/user/detail などのリンクセル
		}
		if htmlquery.FindOne(td, `.//time`) != nil {
			continue // 提出日時セル
		}
		if htmlquery.FindOne(td, `.//span[contains(@class,"label")]`) != nil {
			continue // 結果ラベルセル (AC/WA 等)
		}
		txt := strings.TrimSpace(htmlquery.InnerText(td))
		if txt == "" {
			continue
		}
		if execTeRe.MatchString(txt) || memoryRe.MatchString(txt) {
			continue // 実行時間・メモリ
		}
		if _, err := strconv.Atoi(txt); err == nil {
			continue // 得点・コード長 (数値)
		}
		if strings.HasSuffix(txt, "Byte") || strings.HasSuffix(txt, "Bytes") {
			continue // コード長
		}
		if looksLikeLanguage(txt) {
			return txt
		}
	}
	return ""
}

// looksLikeLanguage は言語名らしさのゆるい判定。verdict ラベルや日時を弾く。
func looksLikeLanguage(txt string) bool {
	if len(txt) > 60 {
		return false
	}
	// 提出日時 "2022-..." や進捗を除外。
	if strings.HasPrefix(txt, "20") && strings.Contains(txt, ":") {
		return false
	}
	return true
}

func parseTime(s string) time.Time {
	for _, layout := range []string{
		"2006-01-02 15:04:05-0700",
		"2006-01-02 15:04:05",
	} {
		if t, err := time.Parse(layout, s); err == nil {
			return t
		}
	}
	return time.Time{}
}

// finalVerdicts は確定 (再取得不要) の結果コード。
var finalVerdicts = map[string]bool{
	"AC": true, "WA": true, "TLE": true, "RE": true, "CE": true,
	"MLE": true, "OLE": true, "QLE": true, "IE": true, "NG": true,
}

// IsFinal は verdict が確定かを返す。WJ/WR/Judging/空 は未確定 (false)。
func IsFinal(verdict string) bool {
	head := strings.Fields(strings.TrimSpace(verdict))
	if len(head) == 0 {
		return false
	}
	return finalVerdicts[head[0]]
}
