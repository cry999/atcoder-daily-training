# >>> atcoder-stat >>>
# started_at  = 2026-09-12T17:57:44+09:00
# solved_at   = 2026-09-12T18:04:17+09:00
# duration_ms = 393264
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import math

N = int(input())
(*P,) = map(int, input().split())

# 選んだコンテストの数 k を見ると、分子だけが変化している。
# 分子だけの最大値を考える。
# k ごとにナイーブに最大値を求めると全体で O(N^3)
# (Q[1], ..., Q[i]) に Q[i+1] を追加することを考えると、変化部分は
# dp[i] * 0.9 + Q[i+1] になっていることがわかる。
# これを利用すれば O(N^2) で求められる。
# NOTE: i を固定した時、k の値は大きい方からやる。小さい方からやると、自分自身を k こ連ねてしまう。

# dp[k] := k このコンテストを選んど時の最大パフォーマンス
dp = [-math.inf] * (N + 1)
dp[0] = 0
for i in range(N):
    for k in range(i + 1, 0, -1):
        dp[k] = max(dp[k], dp[k - 1] * 0.9 + P[i])

ans = -math.inf
d = 0
for k in range(1, N + 1):
    d = 0.9 * d + 1
    ans = max(ans, dp[k] / d - 1200 / math.sqrt(k))
print(ans)
