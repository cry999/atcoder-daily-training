from fractions import Fraction as F
from collections import defaultdict


N, K = map(int, input().split())
points = [tuple(map(int, input().split())) for _ in range(N)]

if K == 1:
    print("Infinity")
    exit()

lines = defaultdict(set)

for i in range(N):
    xi, yi = points[i]
    for j in range(i + 1, N):
        xj, yj = points[j]

        if xi == xj:
            m, a = float("inf"), xi
        else:
            m = F(yi - yj, xi - xj)
            a = yi - xi * m

        lines[(m, a)].add(i)
        lines[(m, a)].add(j)

ans = 0
for points_on_line in lines.values():
    ans += len(points_on_line) >= K
print(ans)
