package ui

import "github.com/charmbracelet/lipgloss"

var (
	headerTitleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("87"))
	keyStyle         = lipgloss.NewStyle().Foreground(lipgloss.Color("245"))
	valueStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("39"))
	caseLabelStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("245"))
	elapsedStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color("245"))
	sectionLabel     = lipgloss.NewStyle().Foreground(lipgloss.Color("245"))

	badgeBase = lipgloss.NewStyle().Bold(true).Width(6).Align(lipgloss.Center)
	passBadge = badgeBase.
			Background(lipgloss.Color("34")).
			Foreground(lipgloss.Color("231"))
	failBadge = badgeBase.
			Background(lipgloss.Color("160")).
			Foreground(lipgloss.Color("231"))
	tleBadge = badgeBase.
			Background(lipgloss.Color("214")).
			Foreground(lipgloss.Color("16"))
	reBadge = badgeBase.
		Background(lipgloss.Color("129")).
		Foreground(lipgloss.Color("231"))

	removedStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("203"))
	addedStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("114"))

	// override / over-limit を強調するためのスタイル
	overrideStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("203")).Bold(true)
	overLimitStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("203")).Bold(true)

	summaryPassStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("114")).Bold(true)
	summaryFailStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("203")).Bold(true)

	infoStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("245")).Italic(true)
)
