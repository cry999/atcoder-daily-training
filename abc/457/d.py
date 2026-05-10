N, K = map(int, input().split())
(*A,) = map(int, input().split())

# 二分探索で実現できる最小値を考える。
MAX = max(A[i] + (i + 1) * K for i in range(N))

lo, hi = min(A), MAX + 1
while hi - lo > 1:
    mi = (lo + hi) // 2

    cost = 0
    for i in range(N):
        cost += max(0, mi - A[i]) // (i + 1)
        cost += max(0, mi - A[i]) % (i + 1) > 0

    if cost <= K:
        lo = mi
    else:
        hi = mi

print(lo)
