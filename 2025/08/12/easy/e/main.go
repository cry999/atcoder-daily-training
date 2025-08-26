package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func unique(s []int) []int {
	seen := make(map[int]bool)
	var result []int
	for _, v := range s {
		if seen[v] {
			continue
		}
		seen[v] = true
		result = append(result, v)
	}
	return result
}

func sum(s []int) int {
	total := 0
	for _, v := range s {
		total += v
	}
	return total
}

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

	// fmt.Println("n:", n, "m:", m)

	var allA [][]int
	for i := 0; i < m; i++ {
		scanner.Scan() // C
		scanner.Scan() // a...
		// fmt.Println("Reading condition", i+1)

		sa := strings.Split(scanner.Text(), " ")
		a := make([]int, len(sa))
		for j := 0; j < len(sa); j++ {
			a[j], err = strconv.Atoi(sa[j])
			if err != nil {
				panic(err)
			}
		}
		allA = append(allA, a)
	}

	var count int
	for i := 0; i < (1 << m); i++ {
		var testA []int
		for j := 0; j < m; j++ {
			// Check if the j-th condition is satisfied
			if i&(1<<j) == 0 {
				continue
			}
			testA = append(testA, allA[j]...)
		}

		uniqueA := unique(testA)
		// fmt.Printf("Testing combination: %010b: %v", i, uniqueA)
		// fmt.Println()

		if sum(uniqueA) == n*(n+1)/2 {
			count++
		}
	}
	fmt.Println(count)
}
