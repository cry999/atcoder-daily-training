N, D = map(int, input().split())
walls = []

for _ in range(N):
    l, r = map(int, input().split())
    walls.append((r, l))

walls.sort()

max_l = 0
ans = 0
for i in range(N):
    r, l = walls[i]
    if l <= max_l:
        # すでに破壊済み
        continue
    # r から r + D -1 までを破壊する
    ans += 1
    max_l = min(10**9, r + D - 1)
print(ans)
