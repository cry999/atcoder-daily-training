# >>> atcoder-stat >>>
# started_at  = 2026-07-07T15:41:44+09:00
# solved_at   = 2026-07-07T15:46:31+09:00
# duration_ms = 287977
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

# 白い部分を数えておく。最後に歩くのに必要な白い部分だけ除いて答えとする。
ans = H * W
for h in range(H):
    ans -= S[h].count("#")

dist = [-1] * (H * W)
q = [0]
dist[0] = 1

ADJ = [(0, -1), (0, 1), (-1, 0), (1, 0)]
for p in q:
    h, w = divmod(p, W)
    for dh, dw in ADJ:
        nh, nw = h + dh, w + dw
        n = nh * W + nw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] == "#":
            continue
        if dist[n] != -1:
            continue
        dist[n] = dist[p] + 1
        q.append(n)

if dist[-1] == -1:
    print(-1)
else:
    print(ans - dist[-1])
