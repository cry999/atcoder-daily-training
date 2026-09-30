# >>> atcoder-stat >>>
# started_at  = 2026-09-30T09:51:41+09:00
# solved_at   = 2026-09-30T10:26:04+09:00
# duration_ms = 2063583
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
H, W, T = map(int, input().split())
A = [list(input()) for _ in range(H)]

pos = []
for h in range(H):
    for w in range(W):
        if A[h][w] == "S":
            pos.append((h, w))

for h in range(H):
    for w in range(W):
        if A[h][w] == "o":
            pos.append((h, w))

for h in range(H):
    for w in range(W):
        if A[h][w] == "G":
            pos.append((h, w))

dist = [-1] * (H * W)
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

N = len(pos)
cost = [[0] * N for _ in range(N)]


def bfs(s: int):
    for p in range(H * W):
        dist[p] = -1

    h, w = pos[s]
    p = h * W + w
    dist[p] = 0

    q = [pos[s]]
    for h, w in q:
        p = h * W + w
        for dh, dw in DIRS:
            nh, nw = h + dh, w + dw
            if not (0 <= nh < H and 0 <= nw < W):
                continue

            if A[nh][nw] == "#":
                continue

            np = nh * W + nw
            if dist[np] != -1:
                continue

            dist[np] = dist[p] + 1
            q.append((nh, nw))

    for t in range(N):
        h, w = pos[t]
        cost[s][t] = cost[t][s] = dist[h * W + w]


# 各ポイント間の距離を計算する。
for s in range(N):
    bfs(s)

# dp[S][i] := 集合 S に含まれる頂点を訪問済みで、頂点 i にいる時の最小移動コスト
INF = 10**18
dp = [[INF] * N for _ in range(1 << N)]
dp[1][0] = 0

for s in range(1 << N):
    for src in range(N):
        if s & (1 << src) == 0:
            continue
        for dst in range(N):
            if s & (1 << dst):
                # 複数回訪問しても意味ないのでスキップ
                continue
            if cost[src][dst] == -1:
                # 到達不可能なのでスキップ
                continue

            ns = s | (1 << dst)
            dp[ns][dst] = min(dp[ns][dst], dp[s][src] + cost[src][dst])

ans = -1
for s in range(1 << N):
    if dp[s][-1] > T:
        continue
    ans = max(ans, s.bit_count() - 2)

print(ans)
