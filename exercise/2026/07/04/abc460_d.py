# >>> atcoder-stat >>>
# started_at  = 2026-07-04T15:16:50+09:00
# solved_at   = 2026-07-04T15:45:34+09:00
# duration_ms = 1724819
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline
H, W = map(int, input().split())
S = [input().rstrip() for _ in range(H)]

INF = 10**18
dist = [INF] * (H * W)

DIRS = [
    [1, 1],
    [1, 0],
    [1, -1],
    [0, 1],
    [0, -1],
    [-1, 1],
    [-1, 0],
    [-1, -1],
]
q = []
for pos in range(H * W):
    h, w = divmod(pos, W)
    if S[h][w] == "#":
        continue

    for dh, dw in DIRS:
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] == "#":
            break
    else:
        continue

    # 近傍に # のある . のみを集める
    q.append(pos)
    dist[pos] = 0

ans = [["."] * W for _ in range(H)]

print(f"[DEBUG] {q=}")
for pos in q:
    h, w = divmod(pos, W)

    for dh, dw in DIRS:
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        npos = nh * W + nw
        if dist[npos] <= dist[pos] + 1:
            continue
        dist[npos] = dist[pos] + 1
        if dist[npos] % 2:
            ans[nh][nw] = "#"
        q.append(npos)

print("\n".join("".join(row) for row in ans))
