package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func main() {
	reader := bufio.NewReaderSize(os.Stdin, 1<<20)
	writer := bufio.NewWriterSize(os.Stdout, 1<<20)
	defer writer.Flush()

	var H, W int
	fmt.Fscan(reader, &H, &W)

	s := make([][]byte, H)
	for i := 0; i < H; i++ {
		var row string
		fmt.Fscan(reader, &row)
		s[i] = []byte(row)
	}

	visited := make([]int, H*W)

	dx := [4]int{0, 0, 1, -1}
	dy := [4]int{1, -1, 0, 0}

	si, sj := 0, 0
	for i := 0; i < H; i++ {
		for j := 0; j < W; j++ {
			if s[i][j] == 'S' {
				si, sj = i, j
			}
		}
	}
	visited[si*W+sj] = 0b1111

	type item struct {
		i, j, prevDir, nextDir int
	}

	stack := make([]item, 0, H*W)
	stack = append(stack, item{si, sj, -1, 0})

	found := false
	for len(stack) > 0 {
		top := &stack[len(stack)-1]
		if top.nextDir >= 4 {
			stack = stack[:len(stack)-1]
			continue
		}
		k := top.nextDir
		top.nextDir++

		i, j, prev := top.i, top.j, top.prevDir
		ni, nj := i+dx[k], j+dy[k]
		if ni < 0 || ni >= H || nj < 0 || nj >= W {
			continue
		}
		nxt := s[ni][nj]
		if nxt == '#' {
			continue
		}
		cur := s[i][j]
		if cur == 'o' && k != prev {
			continue
		}
		if cur == 'x' && k == prev {
			continue
		}
		nidx := ni*W + nj
		if visited[nidx]&(1<<k) != 0 {
			continue
		}
		if nxt == 'o' || nxt == 'x' {
			visited[nidx] |= 1 << k
		} else {
			visited[nidx] = 0b1111
		}

		stack = append(stack, item{ni, nj, k, 0})

		if nxt == 'G' {
			found = true
			break
		}
	}

	if !found {
		fmt.Fprintln(writer, "No")
		return
	}

	fmt.Fprintln(writer, "Yes")
	var sb strings.Builder
	sb.Grow(len(stack) - 1)
	for _, f := range stack[1:] {
		switch f.prevDir {
		case 0:
			sb.WriteByte('R')
		case 1:
			sb.WriteByte('L')
		case 2:
			sb.WriteByte('D')
		default:
			sb.WriteByte('U')
		}
	}
	fmt.Fprintln(writer, sb.String())
}
