V, E = map(int, input().split())

g = [[] for _ in range(V)]
for _ in range(E):
    s, t, d = map(int, input().split())
    g[s].append((t, d))

INF = 10**18
# dp[u][S] := u にいて通過済みの街の状態が S である時の最短距離
dp = [[INF] * (1 << V) for _ in range(V)]
dp[0][1 << 0] = 0


for s in range(1 << V):
    for u in range(V):
        if not s & (1 << u):
            # u は訪れていないといけない
            continue

        for v, d in g[u]:
            if s & (1 << v):
                # v は初訪問でないといけない
                continue
            ns = s | (1 << v)
            dp[v][ns] = min(dp[v][ns], dp[u][s] + d)

ALL = (1 << V) - 1
ans = -1
for u in range(1, V):
    if dp[u][ALL] >= INF:
        continue
    for v, d in g[u]:
        if v != 0:
            continue
        if 0 <= ans <= dp[u][ALL] + d:
            continue
        # print(u, dp[u][ALL], d)
        ans = dp[u][ALL] + d
# print(ans, dp)
print(ans)
