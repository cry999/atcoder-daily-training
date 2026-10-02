# >>> atcoder-stat >>>
# started_at  = 2026-10-02T08:31:55+09:00
# solved_at   = 2026-10-02T08:42:50+09:00
# duration_ms = 655202
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
S = [input() for _ in range(N)]

# プレイヤーそれぞれのいる場所の組み合わせ全てを頂点とするグラフを考える。
# O(N^4)

M = N * N
INF = 10**18

dist = [[INF] * M for _ in range(M)]
players: list[int] = []
for p in range(M):
    x, y = divmod(p, N)
    if S[x][y] == "P":
        players.append(p)

dist[players[0]][players[1]] = 0
q = [tuple(players)]

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

for ps in q:
    for dx, dy in DIRS:
        np = []
        for i in range(2):
            x, y = divmod(ps[i], N)
            nx, ny = x + dx, y + dy
            if not (0 <= nx < N and 0 <= ny < N) or S[nx][ny] == "#":
                # 移動せず
                nx, ny = x, y
            np.append(nx * N + ny)

        if ps == tuple(np):
            # どちらも移動しないならスキップ
            continue
        if dist[np[0]][np[1]] <= dist[ps[0]][ps[1]] + 1:
            # すでに訪問済みならスキップ
            continue
        dist[np[0]][np[1]] = dist[ps[0]][ps[1]] + 1
        q.append(tuple(np))

        if np[0] == np[1]:
            print(dist[np[0]][np[1]])
            break
    else:
        continue
    break
else:
    print(-1)
