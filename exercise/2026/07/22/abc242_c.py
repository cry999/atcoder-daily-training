# >>> atcoder-stat >>>
# started_at  = 2026-07-22T16:57:31+09:00
# solved_at   = 2026-07-22T17:03:45+09:00
# duration_ms = 374260
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353


N = int(input())
dp = [1] * 9

for _ in range(N - 1):
    ndp = [0] * 9
    for x in range(9):
        for y in range(max(0, x - 1), min(x + 2, 9)):
            ndp[y] += dp[x]

    dp = [x % MOD for x in ndp]

print(sum(dp) % MOD)
