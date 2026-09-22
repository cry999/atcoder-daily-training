# >>> atcoder-stat >>>
# started_at  = 2026-09-21T21:43:35+09:00
# solved_at   = 2026-09-21T22:17:07+09:00
# duration_ms = 2012965
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

# u = r+c, v = r-c 座標軸で処理する。

L = 2 * N - 1
ZERO = N - 1

wp = [0] * L  # wp[t] := r+c = t を満たす r, c に対する A[r]*B[c]%M
wm = [0] * L  # wm[t] := r-c = t を満たす r, c に対する A[r]*B[c]%M

for r in range(N):
    for c in range(N):
        # NOTE: wp, wm の和は MOD 取らなくて良い。
        wp[r + c] += A[r] * B[c] % M
        wm[r - c + ZERO] += A[r] * B[c] % M

gp = [0] * L  # gp[x] := sum(A[r]*B[c]%M * |(r+c) - x| for r, c)
gp[0] = sum(t * wp[t] for t in range(L))
sum_wp = sum(wp)

gm = [0] * L  # gm[x] := sum(A[r]*B[c]%M * |(r-c) - x| for r, c)
gm[0] = sum(t * wm[t] for t in range(L))
sum_wm = sum(wm)

pre_p, pre_m = 0, 0
for x in range(L - 1):
    pre_p += wp[x]
    pre_m += wm[x]
    gp[x + 1] = gp[x] + 2 * pre_p - sum_wp
    gm[x + 1] = gm[x] + 2 * pre_m - sum_wm

ans = 0
for i in range(N):
    for j in range(N):
        ans ^= (gp[i + j] + gm[i - j + ZERO]) // 2 + i * N + j
print(ans)
