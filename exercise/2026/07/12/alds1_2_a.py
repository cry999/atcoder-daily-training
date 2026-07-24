def bubble_sort(a: list[int], n: int):
    flag = True
    swaps = 0
    while flag:
        flag = False
        for j in range(n - 1, 0, -1):
            if a[j] < a[j - 1]:
                a[j], a[j - 1] = a[j - 1], a[j]
                flag = True
                swaps += 1
    return swaps


N = int(input())
(*A,) = map(int, input().split())

swaps = bubble_sort(A, N)
print(*A)
print(swaps)
