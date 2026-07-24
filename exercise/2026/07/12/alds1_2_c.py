def selection_sort(A: list[tuple[int, str]], N: int):
    swaps = 0
    for i in range(N):
        minj = i
        for j in range(i, N):
            if A[j][0] < A[minj][0]:
                minj = j
        if i != minj:
            A[i], A[minj] = A[minj], A[i]
            swaps += 1
    return swaps


def bubble_sort(a: list[tuple[int, str]], n: int):
    flag = True
    swaps = 0
    while flag:
        flag = False
        for j in range(n - 1, 0, -1):
            if a[j][0] < a[j - 1][0]:
                a[j], a[j - 1] = a[j - 1], a[j]
                flag = True
                swaps += 1
    return swaps


N = int(input())
S = input().split()
A = []
B = []

for s in S:
    t = s[0]
    n = int(s[1])
    A.append((n, t))
    B.append((n, t))


bubble_sort(A, N)
print(*[f"{t}{n}" for n, t in A])
print("Stable")
selection_sort(B, N)
print(*[f"{t}{n}" for n, t in B])
print("Stable" if A == B else "Not stable")
