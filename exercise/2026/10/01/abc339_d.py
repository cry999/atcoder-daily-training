# >>> atcoder-stat >>>
# started_at  = 2026-10-01T09:18:44+09:00
# solved_at   = 2026-10-01T10:07:48+09:00
# duration_ms = 2944974
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline

N = int(input())
S = [input().rstrip() for _ in range(N)]


players = []
for i in range(N):
    for j in range(N):
        if S[i][j] == "P":
            players.append(i * N + j)

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
INF = 10**18

dist = [[INF] * (N * N) for _ in range(N * N)]
dist[players[0]][players[1]] = 0

q = [(players[0], players[1])]
for p1, p2 in q:
    i1, j1 = divmod(p1, N)
    i2, j2 = divmod(p2, N)
    for di, dj in DIRS:
        ni1, nj1 = i1 + di, j1 + dj
        if not (0 <= ni1 < N and 0 <= nj1 < N) or S[ni1][nj1] == "#":
            ni1, nj1 = i1, j1

        ni2, nj2 = i2 + di, j2 + dj
        if not (0 <= ni2 < N and 0 <= nj2 < N) or S[ni2][nj2] == "#":
            ni2, nj2 = i2, j2

        np1, np2 = ni1 * N + nj1, ni2 * N + nj2
        if np1 == np2:
            print(dist[p1][p2] + 1)
            exit()

        if dist[np1][np2] <= dist[p1][p2] + 1:
            continue
        dist[np1][np2] = dist[p1][p2] + 1
        q.append((np1, np2))
print(-1)
