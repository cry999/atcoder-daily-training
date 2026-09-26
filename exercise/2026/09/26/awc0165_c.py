# >>> atcoder-stat >>>
# started_at  = 2026-09-26T17:06:54+09:00
# solved_at   = 2026-09-26T17:20:24+09:00
# duration_ms = 810146
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


INF = 10**18


N = int(input())
upper = [0] * N
tree = [[] for _ in range(N)]

upper[0] = min(int(input()), 1)
for i in range(1, N):
    p, u = map(int, input().split())
    upper[i] = u
    tree[p - 1].append(i)


def dfs(root: int):
    print(f"[DEBUG] dfs({root=})")
    min_child_salary = INF
    for child in tree[root]:
        min_child_salary = min(min_child_salary, dfs(child))

    upper[root] = min(upper[root], min_child_salary)
    return upper[root]


dfs(0)

if upper[0] < 1:
    print(-1)
else:
    print(sum(upper))
