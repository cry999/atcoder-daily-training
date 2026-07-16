N, W = map(int, input().split())
INF = 10**18
dp = [-INF] * (W + 1)
dp[0] = 0

for _ in range(N):
    v, w, m = map(int, input().split())

    k = 1
    while m > 0:
        k = min(k, m)
        m -= k

        vk = v * k
        wk = w * k
        for ww in range(W, wk - 1, -1):
            dp[ww] = max(dp[ww], dp[ww - wk] + vk)

        k <<= 1

print(max(dp))
