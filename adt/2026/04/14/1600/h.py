from itertools import permutations

N, M = map(int, input().split())
bridges = []
g = [[] for _ in range(N)]

for _ in range(M):
    u, v, t = map(int, input().split())
    u, v = u - 1, v - 1

    bridges.append((u, v, t))
    g[u].append((v, t))
    g[v].append((u, t))

# time[i][j] := 島 i から島 j への最短時間
time = [[float("inf")] * N for _ in range(N)]

for i in range(N):
    time[i][i] = 0

for u, v, t in bridges:
    time[u][v] = min(time[u][v], t)
    time[v][u] = time[u][v]

for k in range(N):
    for i in range(N):
        for j in range(N):
            time[i][j] = min(time[i][j], time[i][k] + time[k][j])

Q = int(input())
for _ in range(Q):
    K = int(input())
    (*B,) = map(lambda x: int(x) - 1, input().split())

    ans = float("inf")
    for perm in permutations(B):  # わたる順番の全パターン
        for s in range(1 << K):  # わたる方向の全パターン
            elapsed, cur = 0, 0
            for k in range(K):
                u, v, t = bridges[perm[k]]
                elapsed += t
                if s & (1 << k):
                    # u -> v
                    elapsed += time[cur][u]
                    cur = v
                else:
                    # v -> u
                    elapsed += time[cur][v]
                    cur = u
            elapsed += time[cur][N - 1]
            ans = min(ans, elapsed)
    print(ans)
