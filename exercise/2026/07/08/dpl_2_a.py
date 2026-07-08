V, E = map(int, input().split())
g = [[] for _ in range(V)]

for _ in range(E):
    s, t, d = map(int, input().split())
    g[s].append((t, d))

INF = 10**18
dp = [[INF] * (1 << V) for _ in range(V)]
dp[0][1] = 0

for s in range(1 << V):
    for u in range(V):
        if dp[u][s] == INF:
            continue
        for v, d in g[u]:
            if s & (1 << v):
                continue
            dp[v][s | (1 << v)] = min(dp[v][s | (1 << v)], dp[u][s] + d)

ans = INF
for u in range(V):
    for v, d in g[u]:
        if v == 0:
            ans = min(ans, dp[u][(1 << V) - 1] + d)
if ans == INF:
    print(-1)
else:
    print(ans)
