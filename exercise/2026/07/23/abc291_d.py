# >>> atcoder-stat >>>
# started_at  = 2026-07-23T12:48:41+09:00
# solved_at   = 2026-07-23T12:54:00+09:00
# duration_ms = 319688
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
cards = [tuple(map(int, input().split())) for _ in range(N)]

# dp[0] := 最後のカードが表を向いている並べ方の総数
# dp[0] := 最後のカードが裏を向いている並べ方の総数
dp = [1] * 2

for i in range(1, N):
    ndp = [0] * 2
    for j in range(2):
        for k in range(2):
            if cards[i][j] != cards[i - 1][k]:
                ndp[j] += dp[k]
    dp = [x % MOD for x in ndp]

print(sum(dp) % MOD)
