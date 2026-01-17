N, K = map(int, input().split())
a = [tuple(map(int, input().split())) for _ in range(N)]

MOD = 10**9 + 7

# dp[u][v][k] := 2^k 回の移動で u から v へ移動する場合の数
dp = [[[0] * (K.bit_length() + 1) for _ in range(N)] for _ in range(N)]

for u in range(N):
    for v in range(N):
        dp[u][v][0] = a[u][v]

# O(N^3 log K)
for k in range(K.bit_length()):
    for u in range(N):
        for v in range(N):
            for i in range(N):
                dp[u][v][k + 1] += dp[u][i][k] * dp[i][v][k]
                dp[u][v][k + 1] %= MOD


# O(N^2 log K)
# K 回の移動で全ての u からの移動方法を足し合わせる。

# dp2[u][k] := 2^k 回の移動で u からの移動の場合の数
dp2 = [[-1] * (K.bit_length() + 1) for _ in range(N)]


def dfs(u: int, K: int) -> int:
    """u から K 回の移動で到達する場合の数を返す"""
    global dp2

    if K == 0:
        return 1

    i = 0
    while K & (1 << i) == 0:
        i += 1

    if dp2[u][i] != -1:
        return dp2[u][i]

    dp2[u][i] = sum(dp[u][v][i] * dfs(v, K ^ (1 << i)) for v in range(N)) % MOD
    return dp2[u][i]


ans = sum(dfs(u, K) for u in range(N)) % MOD
print(ans)
