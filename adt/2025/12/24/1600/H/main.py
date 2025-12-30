from collections import deque

N, M = map(int, input().split())
graph = [[] for _ in range(N + 1)]

for _ in range(M):
    u, v = map(int, input().split())
    graph[u].append((v, 1))
    graph[v].append((u, 1))

S = input()

queue = deque()
dist = [[(float("inf"), -1)] * 2 for _ in range(N + 1)]
for i, c in enumerate(S):
    if c == "S":
        dist[i + 1][0] = (0, i + 1)
        queue.append((i + 1, i + 1))


while queue:
    u, s = queue.popleft()
    if dist[u][0][1] != s and dist[u][1][1] != s:
        continue

    d = dist[u][dist[u][1][1] == s][0]

    for v, c in graph[u]:
        d1, s1 = dist[v][0]
        d2, s2 = dist[v][1]
        if s1 == s:
            if d + c >= d1:
                continue
            dist[v][0] = (d + c, s)
        elif s2 == s:
            if d + c >= d2:
                continue
            dist[v][1] = (d + c, s)
        elif d + c < d1:
            dist[v][1] = (d1, s1)
            dist[v][0] = (d + c, s)
        elif d + c < d2:
            dist[v][1] = (d + c, s)
        else:
            continue

        queue.append((v, s))

for i in range(N):
    if S[i] == "S":
        continue
    print(dist[i + 1][0][0] + dist[i + 1][1][0])
