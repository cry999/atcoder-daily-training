from heapq import heappop as hpop, heappush as hpush

H, W, D = map(int, input().split())
S = [input() for _ in range(H)]

queue = []
for i in range(H):
    for j in range(W):
        if S[i][j] == "H":
            hpush(queue, (-D, i, j))

visited = [[False] * W for _ in range(H)]
pushed = [[False] * W for _ in range(H)]
while queue:
    neg_d, i, j = hpop(queue)
    d = -neg_d
    if visited[i][j]:
        continue
    visited[i][j] = True

    if d == 0:
        # これ以上加湿は広がらない
        continue

    for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        ni, nj = i + di, j + dj
        if not (0 <= ni < H and 0 <= nj < W):
            continue
        if S[ni][nj] == "#":
            continue
        if visited[ni][nj]:
            continue
        if pushed[ni][nj]:
            continue
        pushed[ni][nj] = True
        hpush(queue, (-(d - 1), ni, nj))

print(sum(sum(row) for row in visited))
