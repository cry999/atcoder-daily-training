N, M = map(int, input().split())

# 0 は上空
dist = [[float('inf')]*(N+1) for _ in range(N+1)]
for _ in range(M):
    a, b, c = map(int, input().split())
    dist[a][b] = dist[b][a] = min(dist[a][b], c)

K, T = map(int, input().split())
for d in map(int, input().split()):
    dist[d][0] = T  # 空港 -> 上空はコスト T
    dist[0][d] = 0  # 上空 -> 空港はコスト 0

for i in range(N+1):
    dist[i][i] = 0

for k in range(N+1):
    for i in range(N+1):
        for j in range(N+1):
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])


def append_road(x: int, y: int, t: int):
    if dist[x][y] < t:
        # すでにより低コストな経路があるので対応必要なし
        return
    dist[x][y] = dist[y][x] = t
    for i in range(N+1):
        for j in range(N+1):
            if i == x and j == y:
                continue
            dist[i][j] = min(
                dist[i][j],
                dist[i][x] + dist[x][y] + dist[y][j],
                dist[i][y] + dist[y][x] + dist[x][j],
            )


def append_airport(x: int):
    if dist[x][0] == T:
        # すでに空港があるので対応必要なし
        return
    dist[x][0] = T
    dist[0][x] = 0
    for i in range(N+1):
        for j in range(N+1):
            dist[i][j] = min(
                dist[i][j],
                dist[i][0] + dist[0][x] + dist[x][j],
                dist[i][x] + dist[x][0] + dist[0][j],
            )


Q = int(input())
updated = True
for _ in range(Q):
    *query, = map(int, input().split())
    if len(query) == 4:
        _, x, y, t = query
        append_road(x, y, t)
    elif len(query) == 2:
        _, x = query
        append_airport(x)
    else:
        ans = 0
        for i in range(N):
            for j in range(N):
                if dist[i+1][j+1] == float('inf'):
                    continue
                ans += dist[i+1][j+1]
        print(ans)
        updated = False
