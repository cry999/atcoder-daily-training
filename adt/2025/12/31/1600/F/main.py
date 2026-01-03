from itertools import combinations

N = int(input())
points = [tuple(map(int, input().split())) for _ in range(N)]

ans = 0
for a, b, c in combinations(points, 3):
    if a[0] == b[0]:
        if a[0] == c[0]:
            continue
    else:
        if (c[1] - a[1]) * (b[0] - a[0]) == (b[1] - a[1]) * (c[0] - a[0]):
            continue
    ans += 1

print(ans)
