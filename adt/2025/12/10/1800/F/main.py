N = int(input())
*A, = map(int, input().split())

g = [-1] * N
for i, a in enumerate(A):
    g[i] = a-1

visited = [False]*N
for i in range(N):
    if visited[i]:
        continue

    cur = i
    while not visited[cur]:
        visited[cur] = True
        cur = g[cur]

    B = [cur+1]
    cur = g[cur]
    while cur != B[0]-1:
        B.append(cur+1)
        cur = g[cur]

    print(len(B))
    print(*B)
    break
