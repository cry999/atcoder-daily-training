# >>> atcoder-stat >>>
# started_at  = 2026-08-26T16:51:03+09:00
# solved_at   = 2026-08-26T17:01:17+09:00
# duration_ms = 614200
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
H, W, K = map(int, input().split())
S = [input() for _ in range(H)]

is_safe_row = [all(S[h][w] == "." for w in range(W)) for h in range(H)]
is_safe_col = [all(S[h][w] == "." for h in range(H)) for w in range(W)]

queue = [
    h * W + w for h in range(H) for w in range(W) if is_safe_row[h] and is_safe_col[w]
]

INF = 10**18
dist = [
    0 if is_safe_row[h] and is_safe_col[w] else INF for h in range(H) for w in range(W)
]

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
for p in queue:
    h, w = divmod(p, W)
    print(f"[DEBUG] visit {h=} {w=}, {dist[p]=}")

    for dh, dw in DIRS:
        nh, nw = h + dh, w + dw
        np = nh * W + nw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] == "#":
            continue
        if dist[np] <= dist[p] + 1:
            continue
        dist[np] = dist[p] + 1
        queue.append(np)


ans = sum(dist[p] <= K for p in range(H * W))
print(ans)
