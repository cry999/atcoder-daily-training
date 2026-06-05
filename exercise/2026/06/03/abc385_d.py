from sortedcontainers import SortedList
from collections import defaultdict

N, M, SX, SY = map(int, input().split())

houses_x = defaultdict(SortedList)
houses_y = defaultdict(SortedList)

for _ in range(N):
    x, y = map(int, input().split())
    houses_x[x].add(y)
    houses_y[y].add(x)


x, y = SX, SY
ans = 0
for _ in range(M):
    d, raw_c = input().split()
    c = int(raw_c)

    if d in "UD":
        ny = y + c if d == "U" else y - c

        lo, hi = min(y, ny), max(y, ny)
        i = houses_x[x].bisect_left(lo)
        while i < len(houses_x[x]) and houses_x[x][i] <= hi:
            rm = houses_x[x].pop(i)
            houses_y[rm].remove(x)
            ans += 1

        y = ny

    if d in "LR":
        nx = x - c if d == "L" else x + c

        lo, hi = min(x, nx), max(x, nx)
        i = houses_y[y].bisect_left(lo)
        while i < len(houses_y[y]) and houses_y[y][i] <= hi:
            rm = houses_y[y].pop(i)
            houses_x[rm].remove(y)
            ans += 1

        x = nx

print(x, y, ans)
