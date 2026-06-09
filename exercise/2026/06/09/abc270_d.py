N, K = map(int, input().split())
(*A,) = map(int, input().split())

dp = [0] * (N + 1)
for n in range(N + 1):
    for a in A:
        if n < a:
            break
        # n を目の前にした時、まず a をとると、相手が dp[n-a] をとり
        # 残った (n-a) - dp[n-a] を取れるので、合計
        # a + (n-a) - dp[n-a] = n - dp[n-a] 個が取得できる
        dp[n] = max(dp[n], n - dp[n - a])

print(dp[N])
