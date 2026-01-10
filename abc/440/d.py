import bisect


N, Q = map(int, input().split())
(*A,) = map(int, input().split())

A.sort()
diff = [A[i] - ((A[i - 1] + 1) if i > 0 else 1) for i in range(N)]
cum = [0] * N
cum[0] = diff[0]
for i in range(1, N):
    cum[i] = cum[i - 1] + diff[i]

for _ in range(Q):
    x, y = map(int, input().split())

    i = bisect.bisect_left(A, x)
    if i >= N:
        print(x + y - 1)
        continue
    if A[i] - x >= y:
        print(x + y - 1)
        continue

    offset = A[i] - x
    lo, hi = i, N
    while hi - lo > 1:
        mi = (lo + hi) // 2
        if cum[mi] - cum[i] >= y - offset:
            hi = mi
        else:
            lo = mi
    total = offset + cum[lo] - cum[i]

    if y == total:
        print(A[lo] - 1)
    else:
        print(A[lo] + (y - total))
