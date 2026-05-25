N = int(input())
parts = [tuple(map(int, input().split())) for _ in range(N)]
W = sum(w for w, _, _ in parts)
M = W // 2
dp = [-float("inf")] * (M + 1)
dp[0] = sum(b for _, _, b in parts)

for w, h, b in parts:
    if h <= b:
        # 体の方が価値が高い場合は、頭につけるか試す必要なし
        continue

    for i in range(M, w - 1, -1):
        dp[i] = max(dp[i], dp[i - w] + h - b)
print(max(dp))
