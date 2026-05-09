MAX_H = 10**9
N = int(input())
H = [0] * (N + 1)
H[0] = MAX_H + 2
H[1:] = map(int, input().split())

A = [0] * (N + 1)
A[0] = 1

L = [0] * (N + 1)
L[0] = (H[0], 0)
max_l = 1


for i in range(1, N + 1):
    lo, hi = 0, max_l
    while hi - lo > 1:
        mi = (lo + hi) // 2
        hight, _ = L[mi]
        if hight > H[i]:
            lo = mi
        else:
            hi = mi

    _, j = L[lo]
    A[i] = A[j] + (i - j) * H[i]

    L[hi] = (H[i], i)
    max_l = hi + 1

print(*A[1:])
