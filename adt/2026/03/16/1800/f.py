from sortedcontainers import SortedSet

H, W, N = map(int, input().split())

rows = SortedSet()
cols = SortedSet()

cards = []

for _ in range(N):
    a, b = map(int, input().split())
    rows.add(a)
    cols.add(b)
    cards.append((a, b))

for a, b in cards:
    h = rows.bisect_left(a)
    w = cols.bisect_left(b)

    print(h + 1, w + 1)
