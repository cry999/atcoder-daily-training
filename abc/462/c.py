N = int(input())
points = [tuple(map(int, input().split())) for _ in range(N)]
points.sort()

min_y = float("inf")

ans = 0
for x, y in points:
    if y < min_y:
        min_y = y
        ans += 1
print(ans)
