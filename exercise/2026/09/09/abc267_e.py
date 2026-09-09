# >>> atcoder-stat >>>
# started_at  = 2026-09-09T08:29:10+09:00
# solved_at   = 2026-09-09T08:36:56+09:00
# duration_ms = 466491
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, M = map(int, input().split())
(*A,) = map(int, input().split())

g = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append(v)
    g[v].append(u)

# 重要な考察
# 1. X 以下のコストで操作を完了できるかを X に関する二分探索で調べる。
# 2. X 以下のコストで削除できる頂点を削除可能状態とよぶ。
# 3. 一度削除可能状態になった頂点は、その後の操作に関係なく削除可能状態のまま
# 4. 削除可能状態になった頂点を順番に削除していけば良い。

removed = [False] * N
initial_cost = [sum(A[v] for v in g[u]) for u in range(N)]
cost = initial_cost[:]

lo, hi = -1, max(initial_cost)
while hi - lo > 1:
    x = (lo + hi) // 2

    targets = []
    for i in range(N):
        cost[i] = initial_cost[i]
        removed[i] = cost[i] <= x
        if removed[i]:
            targets.append(i)

    for u in targets:
        for v in g[u]:
            if removed[v]:
                continue
            cost[v] -= A[u]
            if cost[v] <= x:
                removed[v] = True
                targets.append(v)

    if all(removed):
        hi = x
    else:
        lo = x

ans = hi
print(ans)
