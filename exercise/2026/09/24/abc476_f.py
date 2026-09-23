# >>> atcoder-stat >>>
# started_at  = 2026-09-24T07:53:48+09:00
# solved_at   = 2026-09-24T08:02:55+09:00
# duration_ms = 547709
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

L = 2 * N - 1
ZERO = N - 1

wp = [0] * L
wm = [0] * L
for r in range(N):
    for c in range(N):
        wp[r + c] += A[r] * B[c] % M
        wm[r - c + ZERO] += A[r] * B[c] % M

sp, sm = sum(wp), sum(wm)
pre_p, pre_m = 0, 0

gp = [0] * L
gp[0] = sum(wp[t] * t for t in range(L))
gm = [0] * L
gm[0] = sum(wm[t] * t for t in range(L))
for x in range(L - 1):
    pre_p += wp[x]
    pre_m += wm[x]

    gp[x + 1] = gp[x] + 2 * pre_p - sp
    gm[x + 1] = gm[x] + 2 * pre_m - sm

ans = 0
for i in range(N):
    for j in range(N):
        ans ^= (gp[i + j] + gm[i - j + ZERO]) // 2 + i * N + j
print(ans)
