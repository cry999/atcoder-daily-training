import sys

input = sys.stdin.readline

N, M = map(int, input().split())


INF = 10**9

g = [[] for _ in range(N)]
for _ in range(M):
    a, b, c = map(int, input().split())
    g[a - 1].append((b - 1, c))

dist = [[INF] * N for _ in range(N)]

# total_k := s, t をのぞいて k 以下の頂点のみを経由して s から t に移動する全頂点間の移動コスト
total_k = 0
for s in range(N):
    dist[s][s] = 0

    for t, c in g[s]:
        dist[s][t] = c
        total_k += c

# total := sum(total_k, k=0...N-1)
total = 0
for k in range(N):
    for s in range(N):
        for t in range(N):
            new_dist = dist[s][k] + dist[k][t]
            if dist[s][t] > new_dist:
                total_k -= dist[s][t] if dist[s][t] < INF else 0
                total_k += new_dist
                dist[s][t] = new_dist
    total += total_k
print(total)
