package main

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"time"
)

func cmdNew() error {
	y, m, d := time.Now().Local().Date()
	dirname := filepath.Join(
		"exercise",
		fmt.Sprintf("%04d", y),
		fmt.Sprintf("%02d", m),
		fmt.Sprintf("%02d", d),
	)
	if _, err := os.Stat(dirname); errors.Is(err, fs.ErrNotExist) {
		if err := os.MkdirAll(dirname, 0o755); err != nil {
			return fmt.Errorf("failed to create exercise directory: %w", err)
		}
		fmt.Printf("Created new exercise directory: %s\n", dirname)
		return nil
	} else if err != nil {
		return err
	}
	fmt.Printf("Exercise directory already exists: %s\n", dirname)
	return nil
}
