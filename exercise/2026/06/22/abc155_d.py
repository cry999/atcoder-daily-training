from bisect import bisect_left
from bisect import bisect_right

N, K = map(int, input().split())
(*A,) = map(int, input().split())
A.sort()

# X 以下の数はいくつある? -> X についての二分探索


lo, hi = -(10**18 + 1), 10**18 + 1
while hi - lo > 1:
    X = (lo + hi) // 2

    k = 0
    for i, a in enumerate(A):
        if a > 0:
            j = bisect_right(A, X // a, lo=i + 1)
            k += j - i - 1
        elif a < 0:
            j = bisect_left(A, -(X // (-a)), lo=i + 1)
            k += N - j
        elif X >= 0:
            k += N - i - 1

    if k < K:
        lo = X
    else:
        hi = X

print(hi)
