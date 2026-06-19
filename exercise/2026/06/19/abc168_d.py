N, M = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    a, b = map(int, input().split())
    g[a].append(b)
    g[b].append(a)

ans = [-1] * (N + 1)
q = [1]
ans[1] = 0

for u in q:
    for v in g[u]:
        if ans[v] != -1:
            continue
        ans[v] = u
        q.append(v)

print("Yes")
for i in range(2, N + 1):
    print(ans[i])
