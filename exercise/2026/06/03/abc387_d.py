from collections import deque

H, W = map(int, input().split())
S = [input() for _ in range(H)]

si, sj = 0, 0
gi, gj = 0, 0
for i in range(H):
    for j in range(W):
        if S[i][j] == "S":
            si, sj = i, j
        elif S[i][j] == "G":
            gi, gj = i, j

q = deque()
q.append((si, sj, 0, -1))

dist = [[[-1] * 2 for _ in range(W)] for _ in range(H)]

VERT = 0
HORI = 1

DIRS = [(-1, 0, VERT), (1, 0, VERT), (0, -1, HORI), (0, 1, HORI)]

while q:
    i, j, d, prev = q.popleft()

    for di, dj, dir in DIRS:
        ni, nj = i + di, j + dj
        if dir == prev:
            continue
        if not (0 <= ni < H and 0 <= nj < W):
            continue
        if S[ni][nj] == "#":
            continue
        if 0 <= dist[ni][nj][dir] <= d + 1:
            continue
        dist[ni][nj][dir] = d + 1
        if ni == gi and nj == gj:
            break
        q.append((ni, nj, d + 1, dir))
    else:
        continue
    break

print(max(dist[gi][gj]))
