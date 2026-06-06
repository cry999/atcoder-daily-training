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

	removedStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed))
	addedStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen))

	// override / over-limit を強調するためのスタイル
	overrideStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)
	overLimitStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)

	summaryPassStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	summaryFailStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)

	infoStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1)).Italic(true)
)
