from collections import deque

DIGIT = 10

N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    u, v, w = map(int, input().split())
    g[u - 1].append((v - 1, w))

visited = [[False] * (1 << DIGIT) for _ in range(N)]
q = deque()

q.append((0, 0))
visited[0][0] = True

while q:
    u, s = q.popleft()

    for v, w in g[u]:
        if visited[v][s ^ w]:
            continue
        visited[v][s ^ w] = True
        q.append((v, s ^ w))

ans = -1
for i in range(1 << DIGIT):
    if visited[N - 1][i]:
        ans = i
        break

print(ans)
