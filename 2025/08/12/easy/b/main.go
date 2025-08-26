package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func isIncrease(s []int) bool {
	for i := 0; i < len(s)-1; i++ {
		if s[i] >= s[i+1] {
			return false
		}
	}
	return true
}

func isInRange(s []int) bool {
	for _, v := range s {
		if v < 100 || 675 < v {
			return false
		}
	}
	return true
}

func isMultipleOf25(s []int) bool {
	for _, v := range s {
		if v%25 != 0 {
			return false
		}
	}
	return true
}

func main() {
	var s []int
	scanner := bufio.NewScanner(os.Stdin)

	scanner.Scan()
	for _, c := range strings.Split(scanner.Text(), " ") {
		i, err := strconv.Atoi(c)
		if err != nil {
			panic(err)
		}
		s = append(s, i)
	}

	if isIncrease(s) && isInRange(s) && isMultipleOf25(s) {
		fmt.Print("Yes")
	} else {
		fmt.Print("No")
	}
}
