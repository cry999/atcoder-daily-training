from bisect import bisect_left

N, M, D = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())


if N < M:
    A, B = B, A
    N, M = M, N

A.sort()

ans = -1
for b in B:
    i = bisect_left(A, b + D)
    if i < N:
        d = abs(b - A[i])
        if d <= D:
            ans = max(ans, b + A[i])
    if i > 0:
        d = abs(b - A[i - 1])
        if d <= D:
            ans = max(ans, b + A[i - 1])

print(ans)
