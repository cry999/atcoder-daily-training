from collections import deque


N, M = map(int, input().split())

diff = []
for x in range(N):
    for y in range(N, -1, -1):
        if x**2 + y**2 == M:
            diff.append((x, y))

queue = deque()
queue.append((0, 1, 1))

dist = [[float('inf')]*(N+1) for _ in range(N+1)]

while queue:
    d, i, j = queue.popleft()
    if dist[i][j] <= d:
        continue
    dist[i][j] = d
    for si, sj in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        for di, dj in diff:
            ni = i + si*di
            nj = j + sj*dj
            nd = d+1
            if not (1 <= ni <= N and 1 <= nj <= N):
                continue
            if dist[ni][nj] <= nd:
                continue
            queue.append((nd, ni, nj))

for row in dist[1:]:
    print(*map(lambda x: x if x < float('inf') else -1, row[1:]))
