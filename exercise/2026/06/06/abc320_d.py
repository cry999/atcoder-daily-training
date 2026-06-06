N, M = map(int, input().split())
g = [[] for _ in range(N)]
ans = [None] * N

for _ in range(M):
    a, b, x, y = map(int, input().split())
    a, b = a - 1, b - 1
    g[a].append((b, x, y))
    g[b].append((a, -x, -y))

q = [(0, 0, 0)]
ans[0] = (0, 0)

while q:
    u, x, y = q.pop()

    for v, dx, dy in g[u]:
        if ans[v] is not None:
            # 入力は矛盾しないので、確認必要なし
            continue
        nx, ny = x + dx, y + dy
        ans[v] = (nx, ny)
        q.append((v, nx, ny))

for a in ans:
    if a is None:
        print("undecidable")
    else:
        x, y = a
        print(x, y)
