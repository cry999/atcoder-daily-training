from collections import deque

N, M, L, S, T = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    u, v, c = map(lambda x: int(x) - 1, input().split())
    g[u].append((v, c + 1))

q = deque()
q.append((0, 0, 0))  # 頂点, コスト, 通過した辺

reached = [False] * N

while q:
    u, c, l = q.popleft()
    if l == L:
        reached[u] |= S <= c <= T
        continue

    nl = l + 1
    for v, nc in g[u]:
        if reached[v]:
            continue
        nc += c
        if nc + (L - nl) > T:
            continue
        q.append((v, nc, nl))


print(*[i + 1 for i in range(N) if reached[i]])
