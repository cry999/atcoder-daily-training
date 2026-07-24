def selection_sort(A: list[int], N: int):
    swaps = 0
    for i in range(N):
        minj = i
        for j in range(i, N):
            if A[j] < A[minj]:
                minj = j
        if i != minj:
            A[i], A[minj] = A[minj], A[i]
            swaps += 1
    return swaps


N = int(input())
(*A,) = map(int, input().split())

swaps = selection_sort(A, N)
print(*A)
print(swaps)
