N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    a, b, w = map(int, input().split())
    g[a - 1].append((b - 1, w))

# visited[i][w]: 頂点 i に重み w で訪れることができるか？
visited = [[False] * (1 << 10) for _ in range(N)]
visited[0][0] = True

q = [(0, 0)]
while q:
    u, w = q.pop()

    for v, nw in g[u]:
        nw ^= w
        if visited[v][nw]:
            continue
        visited[v][nw] = True
        q.append((v, nw))

ans = -1
for w in range(1 << 10):
    if visited[N - 1][w]:
        ans = w
        break
print(ans)
