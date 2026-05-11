N, K = map(int, input().split())
(*A,) = map(int, input().split())

dp = [0] * (N + 1)

for n in range(1, N + 1):
    for a in A:
        if a > n:
            break
        if a == n:
            dp[n] = a
        else:
            # 1. takahashi が a をとる。
            # 2. aoki は最高スコアの dp[n-a] をとる
            # 3. takahashi は n-a から dp[n-a] をのぞいた分の石をえる
            dp[n] = max(dp[n], n - dp[n - a])

print(dp[N])
