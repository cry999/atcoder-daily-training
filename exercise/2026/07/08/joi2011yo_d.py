# >>> atcoder-stat >>>
# duration_ms = 300000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())

MAX = 20

dp = [0] * (MAX + 1)
dp[A[0]] = 1

for i in range(1, N - 1):
    ndp = [0] * (MAX + 1)
    for j in range(MAX + 1):
        if j + A[i] <= MAX:
            ndp[j + A[i]] += dp[j]
        if j - A[i] >= 0:
            ndp[j - A[i]] += dp[j]
    dp = ndp
print(dp[A[-1]])
