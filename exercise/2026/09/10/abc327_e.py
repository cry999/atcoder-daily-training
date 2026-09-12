# >>> atcoder-stat >>>
# started_at  = 2026-09-10T10:40:27+09:00
# solved_at   = 2026-09-10T10:49:16+09:00
# duration_ms = 529903
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from math import sqrt

N = int(input())
(*P,) = map(int, input().split())

# 重要な考察
# 1. k を固定すれば sum((0.9)^(k-i) Q[i]) の部分だけ変動するのでここに関して DP すれば良い。
# 2. ただし、1 をナイーブに実装すると、O(N^3) になり間に合わない。
# 3. 重要な性質として、(Q1, Q2, ..., Qk) (スコア s) に Q{k+1} を追加した時、分母のスコアは
#   s * 0.9 + Q{k+1} となって、一つ前の最大値を利用できる。
# 4. k の小さい順に DP すれば O(N^2) で解ける。
# 5. 追加する順番には気をつける。

INF = float("inf")

dp = [-INF] * (N + 1)
dp[0] = 0

for i in range(N):
    for k in range(i, -1, -1):
        dp[k + 1] = max(dp[k + 1], 0.9 * dp[k] + P[i])

ans = -INF
denom = 0
for k in range(1, N + 1):
    denom = 0.9 * denom + 1
    ans = max(ans, dp[k] / denom - 1200 / sqrt(k))
print(ans)
