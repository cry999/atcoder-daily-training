# >>> atcoder-stat >>>
# started_at  = 2026-09-08T12:09:09+09:00
# solved_at   = 2026-09-08T12:39:58+09:00
# duration_ms = 1849312
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*A,) = map(int, input().split())

g = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append(v)
    g[v].append(u)

initial_cost = [sum(A[v] for v in g[u]) for u in range(N)]
cost = [initial_cost[u] for u in range(N)]
removed = [False] * N

lo, hi = -1, sum(A) + 1
while hi - lo > 1:
    X = (lo + hi) // 2

    for i in range(N):
        cost[i] = initial_cost[i]
        removed[i] = False

    stack = []
    for u in range(N):
        if cost[u] <= X:
            removed[u] = True
            stack.append(u)

    for u in stack:
        for v in g[u]:
            if removed[v]:
                continue

            cost[v] -= A[u]
            if cost[v] <= X:
                removed[v] = True
                stack.append(v)

    if all(removed):
        hi = X
    else:
        lo = X

print(hi)
