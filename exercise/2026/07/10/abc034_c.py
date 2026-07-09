# >>> atcoder-stat >>>
# started_at  = 2026-07-10T05:55:00+09:00
# solved_at   = 2026-07-10T06:04:12+09:00
# duration_ms = 552028
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
W, H = map(int, input().split())
N = W + H - 2

MOD = 10**9 + 7

inv = [1] * (N + 1)
# a*q + r = 0
# a^-1 = -q*r^-1
for i in range(2, N):
    q, r = divmod(MOD, i)
    inv[i] = (-q * inv[r]) % MOD

M = min(W, H) - 1
# N_C_M を求める
# N_C_M = N! / (M! * (N-M)!)
# N_C_M = N! / ((M-1)! * (N-M+1)!) * (N-M+1) / M
# N_C_M = (N-M+1) / M * N_C_{M-1}
comb = [1] * (M + 1)
for r in range(1, M + 1):
    comb[r] = (comb[r - 1] * (N - r + 1) * inv[r]) % MOD

print(comb[M])
