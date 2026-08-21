# >>> atcoder-stat >>>
# started_at  = 2026-08-16T01:43:45+09:00
# solved_at   = 2026-08-16T01:56:59+09:00
# duration_ms = 794726
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353


N, K = map(int, input().split())
(*A,) = map(int, input().split())

inv = [1] * (N + 1)
for k in range(2, N + 1):
    q, r = divmod(MOD, k)
    inv[k] = (-q * inv[r]) % MOD

co1 = 1
for k in range(1, K):
    co1 = co1 * (N - k) * inv[k] % MOD
co2 = co1 * (K - 1) * inv[N - 1] % MOD

ans = 0
s = 0
for a in A:
    ans += a * a * co1 % MOD
    ans += 2 * s * a * co2 % MOD
    ans %= MOD

    s += a
    s %= MOD

print(ans)
