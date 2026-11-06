from sortedcontainers import SortedList

H, W, N, Q = map(int, input().split())

row = SortedList()
col = SortedList()

for _ in range(N):
    r, c = map(int, input().split())
    row.add(r)
    col.add(c)

for _ in range(Q):
    q, lo, hi = map(int, input().split())

    if q == 1:
        t = row
    else:
        t = col

    i = t.bisect_left(lo)
    j = t.bisect_right(hi)
    print(j - i)
