# >>> atcoder-stat >>>
# started_at  = 2026-08-07T14:58:21+09:00
# solved_at   = 2026-08-07T15:05:57+09:00
# duration_ms = 456340
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*P,) = map(int, input().split())

g = [[] for _ in range(N)]
for i, p in enumerate(P):
    g[p - 1].append(i + 1)

effect = [-1] * (N + 1)
for _ in range(M):
    x, y = map(int, input().split())
    effect[x - 1] = max(effect[x - 1], y)

q = [0]
ans = 0
for u in q:
    if effect[u] >= 0:
        ans += 1
    for v in g[u]:
        effect[v] = max(effect[v], effect[u] - 1)
        q.append(v)
print(ans)
