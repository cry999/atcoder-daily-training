package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)

	scanner.Scan()
	ss := strings.Split(scanner.Text(), " ")
	n, err := strconv.Atoi(ss[0])
	if err != nil {
		panic(err)
	}
	m, err := strconv.Atoi(ss[1])
	if err != nil {
		panic(err)
	}

	var boardS, boardT []string

	for i := 0; i < n; i++ {
		scanner.Scan()
		boardS = append(boardS, scanner.Text())
	}
	for i := 0; i < m; i++ {
		scanner.Scan()
		boardT = append(boardT, scanner.Text())
	}

	for a := 0; a <= n-m; a++ {
		for b := 0; b <= n-m; b++ {
			ok := true

			for i := 0; i < m; i++ {
				if boardS[a+i][b:b+m] != boardT[i] {
					ok = false
					break
				}
			}
			if ok {
				fmt.Println(a+1, b+1)
				return
			}
		}
	}
	fmt.Println("No")
}
