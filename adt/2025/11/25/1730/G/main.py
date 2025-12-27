N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    a, b = map(int, input().split())
    g[a-1].append(b-1)
    g[b-1].append(a-1)

    if len(g[a-1]) > 2 or len(g[b-1]) > 2:
        print('No')
        exit()

visited = [False]*N
for i in range(N):
    if visited[i]:
        continue
    if len(g[i]) == 0:
        visited[i] = True
        continue
    if len(g[i]) == 2:
        continue

    par = -1
    cur = i
    while True:
        if visited[cur]:
            exit()
        visited[cur] = True
        if len(g[cur]) == 0:
            break
        if len(g[cur]) == 1:
            if par == g[cur][0]:
                break
            par, cur = cur, g[cur][0]
            continue
        if len(g[cur]) == 2:
            if par == g[cur][0]:
                par, cur = cur, g[cur][1]
            else:
                par, cur = cur, g[cur][0]
            continue
if any(not v for v in visited):
    print('No')
else:
    print('Yes')
