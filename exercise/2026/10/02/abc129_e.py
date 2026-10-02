# >>> atcoder-stat >>>
# started_at  = 2026-10-02T09:14:05+09:00
# solved_at   = 2026-10-02T09:23:38+09:00
# duration_ms = 573847
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 10**9 + 7

L = input()
dp = [[0] * 2 for _ in range(len(L) + 1)]
dp[0][0] = 1

for i in range(len(L)):
    # less 確定: (a, b) = (0, 1), (1, 0), (0, 0) の追加を試みる
    dp[i + 1][1] += dp[i][1] * 3
    # less 未確定
    s = int(L[i])
    if s == 0:
        # less は確定せず、(a, b) = (0, 0) のみ追加可能
        dp[i + 1][0] += dp[i][0]
    else:
        # (a, b) = (0, 0) の場合は less 確定
        dp[i + 1][1] += dp[i][0]
        # (a, b) = (0, 1), (1, 0) の場合は less 未確定のまま
        dp[i + 1][0] += dp[i][0] * 2

    dp[i + 1][0] %= MOD
    dp[i + 1][1] %= MOD

print(sum(dp[len(L)]) % MOD)
