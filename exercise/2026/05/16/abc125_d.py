N = int(input())
(*A,) = map(int, input().split())

# dp[n][d] := A[n] まで処理が完了して、符号を反転した個数を 2 で割ったあまりが d である時の最大値
dp = [[-float("inf")] * (2) for _ in range(N + 1)]
dp[0][0] = 0

for i in range(N):
    for d in range(2):
        # A[i] を反転させない場合
        dp[i + 1][d] = max(dp[i + 1][d], dp[i][d] + A[i])
        # A[i] を反転させる場合
        dp[i + 1][d] = max(dp[i + 1][d], dp[i][1 - d] - A[i])

# 反転させることができる個数は任意の偶数個である。
print(dp[N][0])
