N = int(input())
(*p,) = map(float, input().split())
# dp[j] = (i-1 枚目までの裏表が決まっているとして) i 枚目の裏表が決まったときに j 枚が表の確率
dp = [0] * (N + 1)
dp[0] = 1

for i in range(N):
    for j in range(i + 1, -1, -1):
        dp[j] *= 1 - p[i]
        if j > 0:
            dp[j] += dp[j - 1] * p[i]
print(sum(dp[N // 2 + 1 :]))
