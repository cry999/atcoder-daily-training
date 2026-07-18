MOD = 998244353

T = int(input())

for _ in range(T):
    N, M = map(int, input().split())
    g = [[] for _ in range(N)]
    dim = [0] * N
    for _ in range(M):
        u, v = map(int, input().split())
        g[u - 1].append(v - 1)
        dim[v - 1] += 1

    path = [0] * N
    path[0] = 1

    q = []
    for i in range(N):
        if dim[i] == 0:
            q.append(i)

    for u in q:
        for v in g[u]:
            path[v] += path[u]
            path[v] %= MOD
            dim[v] -= 1

            if dim[v] == 0:
                q.append(v)

    print(path[N - 1])
