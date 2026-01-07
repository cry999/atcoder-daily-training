N = int(input())
blocks = [tuple(map(int, input().split())) for _ in range(N)]
blocks.sort(key=lambda x: x[0] + x[1])

W = sum(w for w, _, _ in blocks)
dp = [-float("inf")] * (W + 1)
dp[0] = 0
for w, s, v in blocks:
    for pw in range(min(s, W - w), -1, -1):
        dp[pw + w] = max(dp[pw + w], dp[pw] + v)
print(max(dp))
