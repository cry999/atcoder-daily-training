N, M = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    a, b = map(int, input().split())
    g[a].append(b)
    g[b].append(a)

visited = [False] * (N + 1)
for i in range(1, N + 1):
    if visited[i]:
        continue

    visited[i] = True
    q = [(i, -1)]

    is_ok = True

    while q:
        u, p = q.pop()

        if len(g[u]) > 2:
            is_ok = False
            break

        for v in g[u]:
            if v == p:
                continue
            if visited[v]:
                # ループ検出
                is_ok = False
                break
            visited[v] = True
            q.append((v, u))
        else:
            continue
        break

    if not is_ok:
        print("No")
        break
else:
    print("Yes")
