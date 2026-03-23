from itertools import permutations

N, M = map(int, input().split())

dist = [[float("inf")] * N for _ in range(N)]
for i in range(N):
    dist[i][i] = 0

bridges = []
for i in range(M):
    u, v, t = map(int, input().split())
    u, v = u - 1, v - 1
    dist[u][v] = min(dist[u][v], t)
    dist[v][u] = min(dist[v][u], t)
    bridges.append((u, v, t))

# warshall-floyd
for k in range(N):
    for i in range(N):
        for j in range(N):
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

Q = int(input())
for _ in range(Q):
    K = int(input())
    (*B,) = map(lambda x: int(x) - 1, input().split())

    ans = float("inf")
    for bridge_indexes in permutations(B):
        time = 0
        # a := 直前の橋の向きが u -> v だった時の終点 (v) と最小時間
        # b := 直前の橋の向きが v -> u だった時の終点 (u) と最小時間
        ua, ta = 0, 0
        ub, tb = 0, 0
        for i in bridge_indexes:
            u, v, t = bridges[i]

            va = v
            na = min(ta + dist[ua][u], tb + dist[ub][u]) + t

            vb = u
            nb = min(ta + dist[ua][v], tb + dist[ub][v]) + t

            ua, ta = va, na
            ub, tb = vb, nb

        time = min(ta + dist[ua][-1], tb + dist[ub][-1])
        ans = min(ans, time)

    print(ans)
