N, K = map(int, input().split())
(*A,) = map(int, input().split())

# 達成できる最大値を二分探索で求める。

lo, hi = min(A), max(A) + K * N + 1
while hi - lo > 1:
    mi = (lo + hi) // 2

    opnum = 0
    for i in range(N):
        if A[i] >= mi:
            continue
        opnum += (mi - A[i]) // (i + 1)
        opnum += (mi - A[i]) % (i + 1) > 0

    if opnum <= K:
        lo = mi
    else:
        hi = mi

print(lo)
