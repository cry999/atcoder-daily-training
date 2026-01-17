MOD = 10**9 + 7

N, K = map(int, input().split())
graph = [[set() for _ in range(N)] for _ in range(K.bit_length() + 1)]

for u in range(N):
    (*a,) = map(int, input().split())
    for v, ai in enumerate(a):
        if ai:
            graph[0][u].add(v)

for k in range(K.bit_length()):
    for u in range(N):
        for uk in graph[k][u]:
            # u(k): u から 2^k 回移動した到達点
            for ukk in graph[k][uk]:
                # u(k+1): u(k) から 2^k 回移動した到達点
                #       <-> u から 2^(k+1) 回移動した到達点
                graph[k + 1][u].add(ukk)

# dp[k][u][v]: u から 2^k 回移動して v に辿り着く時のパス数
dp = [[[0] * N for _ in range(N)] for _ in range(K.bit_length() + 1)]
for u in range(N):
    for v in graph[0][u]:
        dp[0][u][v] = 1

for k in range(K.bit_length()):
    for u in range(N):
        for v in range(N):
            for via in range(N):
                dp[k + 1][u][v] += dp[k][u][via] * dp[k][via][v]
                dp[k + 1][u][v] %= MOD

ans = [1] * N
k = 0
while K >= (1 << k):
    if not K & (1 << k):
        k += 1
        continue
    ans = [sum(ans[v] * dp[k][u][v] % MOD for v in graph[k][u]) % MOD for u in range(N)]
    k += 1
print(sum(ans) % MOD)
# # k = 10**18 という条件に対応できていない。
#
# dp = [[0] * (K + 1) for _ in range(N)]
# for i in range(N):
#     dp[i][0] = 1
#
# for k in range(K):
#     for u in range(N):
#         dp[u][k + 1] = sum(dp[v][k] for v in graph[u]) % MOD
#
# print(sum(dp[u][K] for u in range(N)) % MOD)
