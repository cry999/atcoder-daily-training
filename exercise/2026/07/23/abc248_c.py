# >>> atcoder-stat >>>
# started_at  = 2026-07-23T16:04:36+09:00
# <<< atcoder-stat <<<
MOD = 998244353

N, M, K = map(int, input().split())

# O(NK) 解法
dp = [1] * (K + 1)
for _ in range(N):
    ndp = [0] * (K + 1)
    for k in range(1, K + 1):
        ndp[k] = dp[k - 1]
        if k - M > 0:
            ndp[k] -= dp[k - M - 1]

    print(f"[DEBUG] {ndp=}")
    dp[0] = ndp[0]
    for k in range(K):
        dp[k + 1] = (dp[k] + ndp[k + 1]) % MOD
    print(f"[DEBUG] {dp=}")

print(dp[K])
