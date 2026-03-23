from itertools import combinations

N = int(input())
points = [tuple(map(int, input().split())) for _ in range(N)]

cnt = 0
for i in combinations(range(N), 3):
    x0, y0 = points[i[0]]
    x1, y1 = points[i[1]]
    x2, y2 = points[i[2]]

    a1, b1 = x1 - x0, y1 - y0
    a2, b2 = x2 - x0, y2 - y0

    s = abs(a1 * b2 - a2 * b1)
    cnt += s > 0

print(cnt)
