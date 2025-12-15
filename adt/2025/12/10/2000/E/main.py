N = int(input())

g = [[] for _ in range(N+1)]
queue = []

for i in range(1, N+1):
    a, b = map(int, input().split())
    if a == b == 0:
        queue.append(i)
    else:
        g[a].append(i)
        g[b].append(i)

acquired = [False] * (N+1)
while queue:
    v = queue.pop()
    if acquired[v]:
        continue

    acquired[v] = True

    for nv in g[v]:
        if acquired[nv]:
            continue
        queue.append(nv)
print(sum(acquired))
