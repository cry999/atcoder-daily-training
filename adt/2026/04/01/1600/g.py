from collections import deque

N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    a, b, w = map(int, input().split())
    g[a - 1].append([b - 1, w])

visited = [[False] * (1 << 10) for _ in range(N)]
visited[0][0] = True
q = deque([(0, 0)])

while q:
    u, s = q.popleft()

    for v, w in g[u]:
        if visited[v][s ^ w]:
            continue
        visited[v][s ^ w] = True
        q.append((v, s ^ w))

for i in range(1 << 10):
    if visited[N - 1][i]:
        print(i)
        break
else:
    print(-1)
