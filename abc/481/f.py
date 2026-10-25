import sys

input = sys.stdin.readline


MOD = 998244353

N, M = map(int, input().split())
g: list[list[tuple[int, int]]] = [[] for _ in range(N)]

for _ in range(M):
    a, b, c = map(int, input().split())
    a -= 1
    b -= 1
    g[a].append((b, c))

ans = [-1] * N
ans[0] = 0

q = [([0], 0)]
for nodes, cost in q:
    cost_groups: list[list[int]] = [[] for _ in range(10)]
    for u in nodes:
        for v, c in g[u]:
            if ans[v] != -1:
                # already visited
                continue
            cost_groups[c].append(v)

    for c in range(1, 10):
        next_nodes: list[int] = []
        next_cost = (cost * 10 + c) % MOD

        for u in cost_groups[c]:
            if ans[u] != -1:
                continue
            ans[u] = next_cost
            next_nodes.append(u)

        if next_nodes:
            q.append((next_nodes, next_cost))

print("\n".join(map(str, ans[1:])))
