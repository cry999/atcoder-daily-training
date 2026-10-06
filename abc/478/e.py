from atcoder.scc import SCCGraph

N, Q = map(int, input().split())
g = SCCGraph(N)
edges = []
for _ in range(Q):
    w, u, v = map(int, input().split())
    u -= 1
    v -= 1
    g.add_edge(u, v)
    edges.append((u, v, w))

groups = g.scc()

K = len(groups)
component = [-1] * N
for c, vs in enumerate(groups):
    for v in vs:
        component[v] = c

g2 = [[] for _ in range(K)]
for u, v, w in edges:
    cu, cv = component[u], component[v]

    if cu != cv:
        g2[cu].append((cv, w))
    elif w == 1:
        print("No")
        exit()

dist = [0] * K
for u in range(K):
    for v, w in g2[u]:
        dist[v] = max(dist[v], dist[u] + w)

A = [dist[component[u]] + 1 for u in range(N)]
print("Yes")
print(*A)
