N = int(input())
(*A,) = map(int, input().split())

graph = [[] for _ in range(N)]

for i in range(N):
    s = input()
    for j in range(N):
        if s[j] == "Y":
            graph[i].append(j)

# dv := dist and values
dv = [[(float("inf"), -float("inf")) for _ in range(N)] for _ in range(N)]
for i in range(N):
    dv[i][i] = (0, 0)
    for j in graph[i]:
        dv[i][j] = (1, A[i])

for k in range(N):
    for i in range(N):
        for j in range(N):
            dij, vij = dv[i][j]
            dik, vik = dv[i][k]
            dkj, vkj = dv[k][j]
            if dij > dik + dkj:
                dv[i][j] = (dik + dkj, vik + vkj)
            elif dij == dik + dkj:
                dv[i][j] = (dij, max(vij, vik + vkj))

Q = int(input())
for _ in range(Q):
    u, v = map(int, input().split())
    dist, val = dv[u - 1][v - 1]
    if dist == float("inf"):
        print("Impossible")
    else:
        print(dist, val + A[v - 1])
