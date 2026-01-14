N, M = map(int, input().split())

graph = [[] for _ in range(N)]

dist = [[(float("inf"), float("inf"))] * N for _ in range(N)]
for i in range(N):
    dist[i][i] = (0, 0)

for _ in range(M):
    a, b, c = map(int, input().split())
    a, b = a - 1, b - 1
    if a > b:
        a, b = b, a

    # グラフは小さい頂点から大きい頂点だけ残しておくほうが
    # 最後の計算で重複がなくて楽。
    graph[a].append((b, c))

    dist[a][b] = dist[b][a] = (c, -1)

# warshal-floyd
for k in range(N):
    for i in range(N):
        for j in range(N):
            d_ik, n_ik = dist[i][k]
            d_kj, n_kj = dist[k][j]
            dist[i][j] = min(dist[i][j], (d_ik + d_kj, n_ik + n_kj))

ans = 0
for i in range(N):
    for j, c in graph[i]:
        d, n = dist[i][j]
        if d < c:
            # 直接つなぐ辺で最短経路でないものは削除して良い。
            ans += 1
        elif d == c and n < -1:
            # 直接つなぐ辺が最短経路でも、直接つなぐ経路以外にも最短経路があるなら
            # いらない。
            ans += 1
# TODO: 最短経路が複数ある場合の考慮
print(ans)
