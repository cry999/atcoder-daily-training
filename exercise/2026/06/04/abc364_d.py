from bisect import bisect_left, bisect_right

N, Q = map(int, input().split())
(*A,) = map(int, input().split())
A.sort()


for _ in range(Q):
    b, k = map(int, input().split())

    lo, hi = -1, 10**14
    while hi - lo > 1:
        mi = (lo + hi) // 2

        i = bisect_left(A, b - mi)
        j = bisect_right(A, b + mi)

        if j - i >= k:
            hi = mi
        else:
            lo = mi

    print(hi)
