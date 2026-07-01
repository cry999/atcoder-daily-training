# >>> atcoder-stat >>>
# started_at  = 2026-07-01T19:32:24+09:00
# solved_at   = 2026-07-01T20:04:17+09:00
# duration_ms = 1913154
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<

H, W, D = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]

cum = [[] for _ in range(D)]
rev = [(-1, -1)] * (H * W + 1)

for p in range(H * W):
    h, w = divmod(p, W)
    rev[A[h][w]] = (h, w)

for d in range(D):
    for p in range(d, H * W + 1, D):
        if p == 0:
            cum[d].append(0)
        elif p - D > 0:
            x0, y0 = rev[p - D]
            x1, y1 = rev[p]
            dx, dy = abs(x1 - x0), abs(y1 - y0)
            cum[d].append(cum[d][-1] + dx + dy)
        else:
            cum[d].append(0)

print(f"[DEBUG] {cum=}")
Q = int(input())
for _ in range(Q):
    l, r = map(int, input().split())
    d = l % D
    ans = cum[d][r // D] - cum[d][l // D]
    print(f"[DEBUG] {d=} {cum[d]=}, {r//D=}, {l//D=}")
    print(ans)
