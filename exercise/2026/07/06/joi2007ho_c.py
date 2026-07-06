import sys

input = sys.stdin.readline

n = int(input())
pillars = [tuple(map(int, input().split())) for _ in range(n)]

pillars_set = set(pillars)

ans = 0
for i, (x0, y0) in enumerate(pillars):
    for j in range(i + 1, n):
        x1, y1 = pillars[j]

        # (x0, y0) と (x1, y1) を結ぶ線から、反時計回りに他の２点がある想定

        x2, y2 = -y1 + y0 + x0, x1 - x0 + y0
        if (x2, y2) not in pillars_set:
            continue

        x3, y3 = x1 - y1 + y0, x1 + y1 - x0
        if (x3, y3) not in pillars_set:
            continue

        ans = max(ans, (x1 - x0) ** 2 + (y1 - y0) ** 2)
print(ans)
