# >>> atcoder-stat >>>
# started_at  = 2026-07-23T15:50:28+09:00
# solved_at   = 2026-07-23T16:04:21+09:00
# duration_ms = 833106
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
X, Y, Z = map(int, input().split())
S = input()

# dp[state] := CapsLock キーの押下状態が state の時の S の最小実現時間
# 1: on / 0: off
# 最初は off なので、dp[1] は INF にしておく。
dp = [0, float("inf")]

key = [Y, X]
for c in S:
    dp = [
        min(dp[0], dp[1] + Z) + key[c == "a"],
        min(dp[1], dp[0] + Z) + key[c == "A"],
    ]

print(min(dp))
