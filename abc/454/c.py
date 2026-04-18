N, M = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    a, b = map(int, input().split())
    g[a].append(b)

q = [1]
acquirable = [False] * (N + 1)
acquirable[1] = True
while q:
    a = q.pop()

    for b in g[a]:
        if acquirable[b]:
            continue
        acquirable[b] = True
        q.append(b)

print(sum(acquirable))
