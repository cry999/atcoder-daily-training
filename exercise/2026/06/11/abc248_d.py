from bisect import bisect_left

N = int(input())
(*A,) = map(int, input().split())

indexes = [[] for _ in range(N + 1)]
for i, a in enumerate(A, start=1):
    indexes[a].append(i)

Q = int(input())
for _ in range(Q):
    L, R, X = map(int, input().split())
    lo = bisect_left(indexes[X], L)
    hi = bisect_left(indexes[X], R + 1)
    print(hi - lo)
