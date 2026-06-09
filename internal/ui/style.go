package ui

import "github.com/charmbracelet/lipgloss"

// Catppuccin Mocha palette (https://catppuccin.com/palette).
const (
	mochaRosewater = "#f5e0dc"
	mochaFlamingo  = "#f2cdcd"
	mochaPink      = "#f5c2e7"
	mochaMauve     = "#cba6f7"
	mochaRed       = "#f38ba8"
	mochaMaroon    = "#eba0ac"
	mochaPeach     = "#fab387"
	mochaYellow    = "#f9e2af"
	mochaGreen     = "#a6e3a1"
	mochaTeal      = "#94e2d5"
	mochaSky       = "#89dceb"
	mochaSapphire  = "#74c7ec"
	mochaBlue      = "#89b4fa"
	mochaLavender  = "#b4befe"
	mochaText      = "#cdd6f4"
	mochaSubtext1  = "#bac2de"
	mochaSubtext0  = "#a6adc8"
	mochaOverlay2  = "#9399b2"
	mochaOverlay1  = "#7f849c"
	mochaOverlay0  = "#6c7086"
	mochaSurface2  = "#585b70"
	mochaSurface1  = "#45475a"
	mochaSurface0  = "#313244"
	mochaBase      = "#1e1e2e"
	mochaMantle    = "#181825"
	mochaCrust     = "#11111b"
)

var (
	headerTitleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color(mochaSapphire))
	keyStyle         = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1))
	valueStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaBlue))
	caseLabelStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1))
	elapsedStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSubtext0))
	sectionLabel     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1))

	badgeBase = lipgloss.NewStyle().Bold(true).Width(6).Align(lipgloss.Center)
	passBadge = badgeBase.
			Background(lipgloss.Color(mochaGreen)).
			Foreground(lipgloss.Color(mochaBase))
	failBadge = badgeBase.
			Background(lipgloss.Color(mochaRed)).
			Foreground(lipgloss.Color(mochaBase))
	tleBadge = badgeBase.
			Background(lipgloss.Color(mochaPeach)).
			Foreground(lipgloss.Color(mochaBase))
	reBadge = badgeBase.
		Background(lipgloss.Color(mochaMauve)).
		Foreground(lipgloss.Color(mochaBase))

	// diff 表示: 行全体の subtle な bg + 変化トークンへの emph、
	// および line number / gutter のスタイル。
	diffMinusBg = "#3a2030" // Mocha Base にうっすら赤を乗せた色 (line bg)
	diffPlusBg  = "#1f3a2a" // 同上、green tint

	// 行番号は前景色を dim neutral に揃え、minus/plus の識別は背景色で行う。
	diffLineNumStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0))
	diffMinusLineNumStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0)).Background(lipgloss.Color(diffMinusBg))
	diffPlusLineNumStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0)).Background(lipgloss.Color(diffPlusBg))
	// gutter (罫線 "│") のスタイル。bg を持つ版は、SBS の center を組み立て
	// るときに各セグメント (bar / padding) が独立に bg を持つよう使う。
	// (lipgloss の nested Render では内側 reset 後に外側 bg が抜けるので、
	// 各セグメントに直接 bg を当てる必要がある。)
	diffGutterStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSurface2))
	diffMinusGutterStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSurface2)).Background(lipgloss.Color(diffMinusBg))
	diffPlusGutterStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSurface2)).Background(lipgloss.Color(diffPlusBg))
	diffMinusLineStyle = lipgloss.NewStyle().Background(lipgloss.Color(diffMinusBg)).Foreground(lipgloss.Color(mochaText))
	diffPlusLineStyle  = lipgloss.NewStyle().Background(lipgloss.Color(diffPlusBg)).Foreground(lipgloss.Color(mochaText))
	// intra-line emph: 差分のあった token を「文字色」で強調する (bg は行 bg
	// と同じ、fg だけ red/green に上書き)。
	diffMinusEmphStyle = lipgloss.NewStyle().Background(lipgloss.Color(diffMinusBg)).Foreground(lipgloss.Color(mochaRed)).Bold(true)
	diffPlusEmphStyle  = lipgloss.NewStyle().Background(lipgloss.Color(diffPlusBg)).Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	// sign: 行頭 "-" / "+" 用 (unified diff) と SBS 中央 sigil 用に共通利用。
	diffMinusSignStyle = lipgloss.NewStyle().Background(lipgloss.Color(diffMinusBg)).Foreground(lipgloss.Color(mochaRed)).Bold(true)
	diffPlusSignStyle  = lipgloss.NewStyle().Background(lipgloss.Color(diffPlusBg)).Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	diffContextStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1)) // -v 時の context (マッチ行)。背景なし dim foreground

	// override / over-limit を強調するためのスタイル
	overrideStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)
	overLimitStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)

	summaryPassStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	summaryFailStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)

	infoStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1)).Italic(true)
)
