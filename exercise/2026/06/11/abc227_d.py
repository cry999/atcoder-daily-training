N, K = map(int, input().split())
(*A,) = map(int, input().split())

lo, hi = 1, sum(A) // K + 1
while hi - lo > 1:
    mi = (lo + hi) // 2
    if sum(min(A[i], mi) for i in range(N)) >= mi * K:
        lo = mi
    else:
        hi = mi
print(lo)
