N, M = map(int, input().split())
graph = [[] for _ in range(N)]

for _ in range(M):
    a, b = map(int, input().split())
    a, b = a - 1, b - 1
    graph[a].append(b)
    graph[b].append(a)

ans = []
for i in range(N):
    n = len(graph[i])
    a = N - n - 1

    ans.append(a * (a - 1) * (a - 2) // 6)
print(*ans)
