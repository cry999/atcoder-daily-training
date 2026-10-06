# >>> atcoder-stat >>>
# started_at  = 2026-10-03T10:49:59+09:00
# solved_at   = 2026-10-03T11:00:27+09:00
# duration_ms = 628519
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N = int(input())
S = [input().rstrip() for _ in range(N)]

M = N * N

players = []
for p in range(M):
    h, w = divmod(p, N)
    if S[h][w] == "P":
        players.append(p)

INF = 10**18
dist = [[INF] * M for _ in range(M)]
dist[players[0]][players[1]] = 0

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

q = [tuple(players)]
for ps in q:
    for dh, dw in DIRS:
        np = []
        for p in ps:
            h, w = divmod(p, N)

            nh, nw = h + dh, w + dw
            if not (0 <= nh < N and 0 <= nw < N):
                nh, nw = h, w
            if S[nh][nw] == "#":
                nh, nw = h, w
            np.append(nh * N + nw)

        np = tuple(np)
        if np == ps:
            continue
        if dist[np[0]][np[1]] <= dist[ps[0]][ps[1]] + 1:
            continue

        dist[np[0]][np[1]] = dist[ps[0]][ps[1]] + 1
        q.append(np)
        if np[0] == np[1]:
            print(dist[np[0]][np[1]])
            exit()
print(-1)
