N = int(input())

g = [[] for _ in range(N+1)]
v = [False] * (N+1)
queue = []
cnt = 0
for n in range(1, N+1):
    a, b = map(int, input().split())
    if a and b:
        g[a].append(n)
        g[b].append(n)
    else:
        queue.append(n)
        v[n] = True
        cnt += 1

while queue:
    n = queue.pop()
    for u in g[n]:
        if v[u]:
            continue
        queue.append(u)
        v[u] = True
        cnt += 1

print(cnt)
