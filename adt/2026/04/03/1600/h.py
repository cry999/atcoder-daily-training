N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*C,) = map(int, input().split())
(*X,) = map(int, input().split())

# cost[i][j] := 商品 i を i 未満の商品を j 個購入する場合に購入する際の費用
# ただし、買う順番は問わないことに注意。
cost = [[0] * N for _ in range(N)]

cost[0][0] = C[0]
for i in range(1, N):
    for j in range(i + 1):
        cost[i][j] = C[i - j]
        if j > 0:
            cost[i][j] = min(cost[i][j], cost[i][j - 1])

dp = [[float("inf")] * (N + 1) for _ in range(N + 1)]
dp[0][0] = 0

must_buy = [False] * N
for x in X:
    must_buy[x - 1] = True

for i in range(N):
    for j in range(i + 1):
        # 商品 i を購入する場合
        dp[i + 1][j + 1] = min(dp[i + 1][j + 1], dp[i][j] + A[i] + cost[i][j])
        # 商品 i を購入しない場合 (X に含まれていない場合)
        if must_buy[i]:
            continue
        dp[i + 1][j] = min(dp[i + 1][j], dp[i][j])

print(min(dp[N]))
