MOD = 998244353

N, M, K, S, T, X = map(int, input().split())
graph = [[] for _ in range(N + 1)]

for _ in range(M):
    u, v = map(int, input().split())
    graph[u].append(v)
    graph[v].append(u)

# dp[d][k][n] := 頂点 n から k 回の移動で X の利用回数を 2 で割ったあまりが d である
#               T に辿り着く方法の数
dp = [[[0] * (N + 1) for _ in range(K + 1)] for _ in range(2)]
dp[0][0][T] = 1
for k in range(1, K + 1):
    for u in range(1, N + 1):
        for v in graph[u]:
            for d in range(2):
                if v == X:
                    dp[1 - d][k][v] += dp[d][k - 1][u]
                    dp[1 - d][k][v] %= MOD
                else:
                    dp[d][k][v] += dp[d][k - 1][u]
                    dp[d][k][v] %= MOD

print(dp[0][K][S])
