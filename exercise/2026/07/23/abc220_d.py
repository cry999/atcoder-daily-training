# >>> atcoder-stat >>>
# started_at  = 2026-07-23T10:58:00+09:00
# solved_at   = 2026-07-23T11:02:53+09:00
# duration_ms = 293206
# target_ms   = 900000
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
(*A,) = map(int, input().split())

# dp[x] := 左端が x である場合の数
dp = [0] * 10
dp[A[0]] = 1

for i in range(1, N):
    ndp = [0] * 10

    y = A[i]
    for x in range(10):
        ndp[(x + y) % 10] += dp[x]
        ndp[(x * y) % 10] += dp[x]

    dp = [x % MOD for x in ndp]

print(*dp, sep="\n")
