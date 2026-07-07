# >>> atcoder-stat >>>
# started_at  = 2026-07-07T08:11:46+09:00
# solved_at   = 2026-07-07T08:15:28+09:00
# duration_ms = 222185
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

sys.setrecursionlimit(10**6)

input = sys.stdin.readline

N, Q = map(int, input().split())
g = [[] for _ in range(N)]
for _ in range(N - 1):
    a, b = map(int, input().split())
    a, b = a - 1, b - 1
    g[a].append(b)
    g[b].append(a)

counter = [0] * N

for _ in range(Q):
    p, x = map(int, input().split())
    counter[p - 1] += x


def dfs(u: int, p: int = -1, c: int = 0):
    counter[u] += c
    for v in g[u]:
        if v == p:
            continue
        dfs(v, u, counter[u])
    return


dfs(0)

print(*counter)
