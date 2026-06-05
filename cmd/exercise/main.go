package main

import (
	"fmt"
	"os"
	"path/filepath"
	"time"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: exercise <problem>")
		os.Exit(1)
	}

	switch os.Args[1] {
	case "new":
		y, m, d := time.Now().Local().Date()
		dirname := filepath.Join(
			"exercise",
			fmt.Sprintf("%04d", y),
			fmt.Sprintf("%02d", m),
			fmt.Sprintf("%02d", d),
		)
		if err := os.MkdirAll(dirname, 0o755); err != nil {
			fmt.Printf("Failed to new exercise directory: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Created new exercise directory: %s\n", dirname)
	}
}
