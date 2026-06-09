from collections import deque
from math import isqrt

N, M = map(int, input().split())

dirs = []

SIGNS = ((1, 1), (1, -1), (-1, 1), (-1, -1))

for di in range(0, M):
    if di * di > M:
        break

    dj2 = M - di * di
    dj = isqrt(dj2)

    if dj < di:
        break

    if dj * dj == dj2:
        for si, sj in SIGNS:
            dirs.append((si * di, sj * dj))
            if di != dj:
                dirs.append((si * dj, sj * di))

# print(dirs)

dist = [-1] * (N * N)
dist[0] = 0

q = deque()
q.append(0)

while q:
    pos = q.popleft()
    i, j = divmod(pos, N)
    d = dist[pos]

    for di, dj in dirs:
        ni, nj = i + di, j + dj
        npos = ni * N + nj
        nd = d + 1

        if not (0 <= ni < N and 0 <= nj < N):
            continue
        if 0 <= dist[npos] <= nd:
            continue
        dist[npos] = nd
        q.append(npos)

for i in range(N):
    print(*dist[i * N : (i + 1) * N])
