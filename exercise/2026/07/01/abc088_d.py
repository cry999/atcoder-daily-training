# >>> atcoder-stat >>>
# started_at  = 2026-07-01T20:11:11+09:00
# solved_at   = 2026-07-01T20:15:21+09:00
# duration_ms = 250247
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
H, W = map(int, input().split())
S = [input() for _ in range(H)]

dist = [-1] * (H * W)
dist[0] = 1
q = [0]
for p in q:
    h, w = divmod(p, W)
    for dh, dw in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        np = nh * W + nw
        if S[nh][nw] == "#" or dist[np] != -1:
            continue
        dist[np] = dist[p] + 1
        q.append(np)

whites = 0
for p in range(H * W):
    h, w = divmod(p, W)
    whites += S[h][w] == "."

if dist[-1] == -1:
    print(-1)
else:
    print(whites - dist[-1])
