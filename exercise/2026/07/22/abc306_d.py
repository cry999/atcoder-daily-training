# >>> atcoder-stat >>>
# started_at  = 2026-07-22T18:33:41+09:00
# solved_at   = 2026-07-22T18:39:44+09:00
# duration_ms = 363978
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

FINE = 0
POISON = 1
# dp[h] := 健康状態が h の時のおいしさの最大値
dp = [0] * 2

for i in range(N):
    x, y = map(int, input().split())
    ndp = [0] * 2
    if x == 0:  # 解毒剤いり
        ndp[FINE] = max(dp[FINE], max(dp) + y)
        ndp[POISON] = dp[POISON]  # 下げてもらう
    else:  # 毒入り
        ndp[FINE] = dp[FINE]  # 下げてもらう
        ndp[POISON] = max(dp[FINE] + y, dp[POISON])

    dp = ndp

print(max(dp))
