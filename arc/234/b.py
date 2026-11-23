N, M, Q = map(int, input().split())
S = input()

g: list[list[int]] = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append(v)
    g[v].append(u)

y = [-1] * N
y[0] = 1

u0 = g[0][0]
y[u0] = 2

q = [(0, u0), (u0, 0)]
for u, v in q:
    for w in g[v]:
        if y[w] == -1:
            y[w] = y[u] ^ y[v]
            q.append((v, w))

# print(y)

vv = {0}

for u in range(N):
    if len(g[u]) < 2:
        continue

    a = g[u][0]
    for b in g[u][1:]:
        c = y[a] ^ y[u] ^ y[b]
        vv |= {x ^ c for x in vv}

s = 0
for u in range(N):
    if S[u] == "1":
        s ^= y[u]

yesno = ["No", "Yes"]
for _ in range(Q):
    x = int(input()) - 1
    s ^= y[x]
    print(yesno[s in vv])
