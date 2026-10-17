# >>> atcoder-stat >>>
# started_at  = 2026-10-10T15:18:45+09:00
# solved_at   = 2026-10-10T15:35:18+09:00
# duration_ms = 993553
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
from sortedcontainers import SortedList

input = sys.stdin.readline
sys.setrecursionlimit(10**6)


N, Q = map(int, input().split())
(*X,) = map(int, input().split())

g = [[] for _ in range(N)]
for _ in range(N - 1):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    g[a].append(b)
    g[b].append(a)

queries = [[] for _ in range(N)]
for i in range(Q):
    v, k = map(int, input().split())
    v -= 1
    queries[v].append((k, i))

ans = [0] * Q


# 方針
# DFS で葉の方から query に答えていく。
def dfs(u: int, p: int = -1):
    res = SortedList([X[u]])
    for v in g[u]:
        if v == p:
            continue
        child = dfs(v, u)
        if len(child) > len(res):
            res, child = child, res
        res.update(child)

    for k, i in queries[u]:
        ans[i] = res[-k]

    return res


dfs(0)

print("\n".join(map(str, ans)))
