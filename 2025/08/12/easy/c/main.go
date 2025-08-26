package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()

	n, err := strconv.Atoi(scanner.Text())
	if err != nil {
		panic(err)
	}
	pow, k := 1, 0
	for pow <= n {
		if pow > n {
			break
		}
		pow <<= 1
		k++
	}
	fmt.Println(k - 1)
}
