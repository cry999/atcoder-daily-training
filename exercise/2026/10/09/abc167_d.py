# >>> atcoder-stat >>>
# started_at  = 2026-10-09T18:37:34+09:00
# solved_at   = 2026-10-09T18:42:20+09:00
# duration_ms = 286821
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K = map(int, input().split())
(*A,) = map(int, input().split())

M = K.bit_length()

# dp[i][j] := 街 i から 2^j 回の移動で到達する街
dp = [[0] * (M + 1) for _ in range(N)]
for i in range(N):
    dp[i][0] = A[i] - 1

for j in range(1, M + 1):
    for i in range(N):
        dp[i][j] = dp[dp[i][j - 1]][j - 1]


ans = 0
for j in range(M + 1):
    if (K >> j) & 1:
        ans = dp[ans][j]
print(ans + 1)
