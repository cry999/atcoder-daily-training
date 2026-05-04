MOD = 998244353

N, M, K = map(int, input().split())
# g[u]: 頂点 u から繋がって**いない**頂点
g = [[] for _ in range(N)]

for _ in range(M):
    u, v = map(lambda x: int(x) - 1, input().split())
    g[u].append(v)
    g[v].append(u)

# 自分自身も繋がっていないことに注意
for u in range(N):
    g[u].append(u)

dp = [[0] * (K + 1) for _ in range(N)]
dp[0][0] = 1

for k in range(K):
    # print(f"=== {k=} ===")
    s = 0
    for u in range(N):
        s += dp[u][k]
        s %= MOD
    # print(f"  {s=}")

    for u in range(N):
        dp[u][k + 1] = s
        for v in g[u]:
            # print(f"  {u=} -x-> {v=}: ({dp[v][k]})")
            dp[u][k + 1] -= dp[v][k]
            dp[u][k + 1] %= MOD

print(dp[0][K])
# print(dp)
