# >>> atcoder-stat >>>
# duration_ms = 600000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<

D, N = map(int, input().split())
# 温度
T = [int(input()) for _ in range(D)]
A = [0] * N
B = [0] * N
C = [0] * N
for i in range(N):
    A[i], B[i], C[i] = map(int, input().split())

# d 日目に服 iを来た時の d 日目までの最大合計スコア
dp = [0 if A[i] <= T[0] <= B[i] else -1 for i in range(N)]

for d in range(1, D):
    ndp = [-1] * N
    for i in range(N):  # 前日来ていた服
        if dp[i] < 0:
            continue
        for j in range(N):  # 今日着る服
            if not A[j] <= T[d] <= B[j]:
                continue
            ndp[j] = max(ndp[j], dp[i] + abs(C[j] - C[i]))
    dp = ndp
print(max(dp))
