import sys

sys.setrecursionlimit(10**7)
input = sys.stdin.readline


N, M, L, S, T = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    u, v, c = map(int, input().split())
    g[u].append((v, c))


ans = [False] * (N + 1)
q = [(1, 0, 0)]

while q:
    u, step, cost = q.pop()
    if step == L:
        if S <= cost <= T:
            ans[u] = True
        continue

    for v, c in g[u]:
        nc = cost + c
        if nc > T:
            continue
        q.append((v, step + 1, nc))


print(" ".join(map(str, [i for i in range(N + 1) if ans[i]])))
