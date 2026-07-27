# >>> atcoder-stat >>>
# started_at  = 2026-07-27T22:04:59+09:00
# solved_at   = 2026-07-27T22:14:50+09:00
# duration_ms = 591321
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# missed      = true
# <<< atcoder-stat <<<
N = int(input())
(*S,) = map(int, input())
(*C,) = map(int, input().split())

INF = float("inf")
# dp[k][n] := 処理済みの文字列において、隣接する数字が等しいペアの数が k で末尾が n である数字の最小コスト
dp = [[INF] * 2 for _ in range(2)]
dp[0][S[0]] = 0
dp[0][1 - S[0]] = C[0]

for i in range(1, N):
    ndp = [[INF] * 2 for _ in range(2)]

    ndp[0][S[i]] = dp[0][1 - S[i]]
    ndp[0][1 - S[i]] = dp[0][S[i]] + C[i]

    ndp[1][S[i]] = min(dp[1][1 - S[i]], dp[0][S[i]])
    ndp[1][1 - S[i]] = min(dp[1][S[i]], dp[0][1 - S[i]]) + C[i]

    dp = ndp

print(min(dp[1]))

# 前後から文字列を扱う方法
# # left[i][n] := i 文字目が n になるように、1~i 文字目までを 0 と 1 が交互になるように並べるコスト
# left = [[0] * 2 for _ in range(N)]
# left[0][1 - S[0]] = C[0]
# # right[i][n] := i 文字目が n になるように、i~N 文字目までを 0 と 1 が交互になるように並べるコスト
# right = [[0] * 2 for _ in range(N)]
# right[-1][1 - S[-1]] = C[-1]
#
# for i in range(1, N):
#     left[i][0] = left[i - 1][1]
#     left[i][1] = left[i - 1][0]
#
#     left[i][1 - S[i]] += C[i]
#
# for i in range(N - 1, 0, -1):
#     right[i - 1][0] = right[i][1]
#     right[i - 1][1] = right[i][0]
#
#     right[i - 1][1 - S[i - 1]] += C[i - 1]
#
# ans = min(
#     min(left[i][0] + right[i + 1][0], left[i][1] + right[i + 1][1])
#     for i in range(N - 1)
# )
# print(f"[DEBUG] {left=}")
# print(f"[DEBUG] {right=}")
# print(ans)
