# >>> atcoder-stat >>>
# started_at  = 2026-07-10T07:16:25+09:00
# solved_at   = 2026-07-10T07:23:38+09:00
# duration_ms = 433973
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
N = int(input())
K = int(input())

MOD = 10**9 + 7

# K-1 個の等号 or 不等号を置く場所にいくつ等号をおけるか
# 不等号を k 個おくと、数字は 1~N から k+1 個選ぶことになる。
# したがって、{K-1}_C_{k} * {N}_C_{k+1} を k について足し合わせれば良い。

M = max(N, K)
inv = [1] * (M + 1)
for i in range(2, M + 1):
    q, r = divmod(MOD, i)
    inv[i] = (-q * inv[r]) % MOD

# {K-1}_C_{k} を求める
comb_k = [1] * K
for r in range(1, K):
    comb_k[r] = (comb_k[r - 1] * (K - 1 - r + 1) * inv[r]) % MOD

# {N}_C_{k+1} を求める
comb_n = [1] * (N + 1)
for r in range(1, N + 1):
    comb_n[r] = (comb_n[r - 1] * (N - r + 1) * inv[r]) % MOD

ans = 0
for k in range(min(K, N)):
    ans = (ans + comb_k[k] * comb_n[k + 1]) % MOD
print(ans)
