V, E = map(int, input().split())
g = [[] for _ in range(V)]

for _ in range(E):
    s, t, d = map(int, input().split())
    g[s].append((t, d))

# dp[u][S] := 街の訪問状況が S で今 u にいる場合の最短移動距離。
INF = float("inf")
dp = [[INF] * (1 << V) for _ in range(V)]
dp[0][1 << 0] = 0

for s in range(1 << V):  # 現在の訪問状況
    for u in range(V):  # 現在いるまち候補
        if s & (1 << u) == 0:
            # 未訪問なら現在いるはずがない
            continue

        for v, d in g[u]:  # 次の訪れる街の候補
            if s & (1 << v) != 0:
                # すでに訪問ずみならもう訪れない
                continue
            ns = s | (1 << v)
            # 最短距離を更新できるなら更新する
            dp[v][ns] = min(dp[v][ns], dp[u][s] + d)
ALL = (1 << V) - 1
ans = INF
for u in range(V):
    # 各街から全ての街を訪問した後に 1 に戻ってくる最短を考える。
    for v, d in g[u]:
        if v != 0:
            # 1 に戻ってくる経路だけが対象
            continue
        # print(f"[DEBUG] {u=} -> {v=}: {dp[u][ALL]}+{d}")
        ans = min(ans, dp[u][ALL] + d)
print(ans if ans < INF else -1)
