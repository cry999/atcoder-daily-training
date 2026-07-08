# >>> atcoder-stat >>>
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
# N: 都市のかず, M: 日程
N, M = map(int, input().split())
# D[i] := city[i] と city[i] の距離
D = [int(input()) for _ in range(N)]
# C[i] := 日程[i]のコンディション
C = [int(input()) for _ in range(M)]

INF = 10**18
# dp[i][d] := d 日目に都市 i にいる時の疲労度
dp = [[INF] * (M + 1) for _ in range(N + 1)]
for d in range(M + 1):
    dp[0][d] = 0

for i in range(N):
    for d in range(M):
        dp[i + 1][d + 1] = min(dp[i + 1][d], dp[i][d] + D[i] * C[d])
print(dp[N][M])
