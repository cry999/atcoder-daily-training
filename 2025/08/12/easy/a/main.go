package main

import (
	"bufio"
	"bytes"
	"fmt"
	"os"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	var board [][]byte
	for scanner.Scan() {
		b := bytes.TrimSuffix(scanner.Bytes(), []byte{'\n'})
		board = append(board, b)
	}

	checkRow := func(i, j int) bool {
		if board[i][j] != '#' {
			return true
		}
		switch i {
		case 0:
			return board[1][j] == '#'
		case 1: // 1
			return board[0][j] == '#'
		}
		return false
	}
	checkCol := func(i, j int) bool {
		if board[i][j] != '#' {
			return true
		}
		switch j {
		case 0:
			return board[i][1] == '#'
		case 1:
			return board[i][0] == '#'
		}
		return false
	}
	check := func(i, j int) bool {
		return checkRow(i, j) || checkCol(i, j)
	}

	checkAll := true
	for i, row := range board {
		for j, col := range row {
			if col != '#' {
				continue
			}

			if !check(i, j) {
				checkAll = false
			}
		}
	}
	switch checkAll {
	case true:
		fmt.Println("Yes")
	default:
		fmt.Println("No")
	}
}
