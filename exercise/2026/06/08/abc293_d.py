N, M = map(int, input().split())
g = [[] for _ in range(2 * N)]

for i in range(N):
    u = 2 * i
    v = 2 * i + 1

    g[u].append((v, -1))
    g[v].append((u, -1))

for i in range(M):
    raw_a, b, raw_c, d = input().split()
    a = int(raw_a) - 1
    c = int(raw_c) - 1

    u = 2 * a + (b == "B")
    v = 2 * c + (d == "B")

    g[u].append((v, i))
    g[v].append((u, i))

visited = [False] * (2 * N)
circle, non_circle = 0, 0
for i in range(N):
    if visited[2 * i]:
        continue
    # print("[DEBUG] start", 2 * i)

    visited[2 * i] = True
    visited[2 * i + 1] = True
    is_circle = False
    q = [(2 * i, 2 * i + 1, -1), (2 * i + 1, 2 * i, -1)]
    while q:
        u, p, ei = q.pop()
        for v, ej in g[u]:
            if v == p and ei == ej:
                continue
            if visited[v]:
                is_circle = True
                continue
            visited[v] = True
            q.append((v, u, ej))

    # print("[DEBUG] end", 2 * i, "is_circle =", is_circle)
    if is_circle:
        circle += 1
    else:
        non_circle += 1

print(circle, non_circle)
