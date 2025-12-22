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


changes = []


def append_road(x: int, y: int, t: int):
    global changes
    if dist[x][y] < t:
        # すでにより低コストな経路があるので対応必要なし
        return
    old = dist[x][y]
    dist[x][y] = dist[y][x] = t
    changes.append((x, y, old, t))
    changes.append((y, x, old, t))
    for i in range(N+1):
        for j in range(N+1):
            if i == x and j == y:
                continue
            old = dist[i][j]
            dist[i][j] = min(
                dist[i][j],
                dist[i][x] + dist[x][y] + dist[y][j],
                dist[i][y] + dist[y][x] + dist[x][j],
            )
            if old != dist[i][j]:
                changes.append((i, j, old, dist[i][j]))


def append_airport(x: int):
    global changes
    if dist[x][0] == T:
        # すでに空港があるので対応必要なし
        return
    dist[x][0] = T
    dist[0][x] = 0
    for i in range(N+1):
        for j in range(N+1):
            old = dist[i][j]
            dist[i][j] = min(
                dist[i][j],
                dist[i][0] + dist[0][x] + dist[x][j],
                dist[i][x] + dist[x][0] + dist[0][j],
            )
            if old != dist[i][j]:
                changes.append((i, j, old, dist[i][j]))


Q = int(input())
S = sum(
    dist[i][j] if dist[i][j] != float('inf') else 0
    for i in range(1, N+1) for j in range(1, N+1)
)
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
        # print('query 3')
        for i, j, old, new in changes:
            # 頂点0（上空）を含むペアは集計対象外
            if i == 0 or j == 0:
                continue
            # print(f'  {old=}, {new=}')
            if old == float('inf'):
                S += new
            else:
                S += new-old
        print(S)
        changes = []
