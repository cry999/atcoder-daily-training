import sys
from sortedcontainers import SortedList

sys.setrecursionlimit(10**7)

N = int(input())
(*A,) = map(int, input().split())

g = [[] for _ in range(N)]

for _ in range(N - 1):
    u, v = map(lambda x: int(x) - 1, input().split())
    g[u].append(v), g[v].append(u)


ans = [False] * N
stack = SortedList()


def dfs(u: int, p: int = -1, yes: bool = False):
    # print(f"dfs: {u=}, {p=}, {yes=}")
    # print(f"  {stack=}")
    if yes:
        ans[u] = True
    else:
        a = A[u]
        ans[u] = a in stack
        stack.add(a)

    for v in g[u]:
        if p == v:
            continue
        dfs(v, u, ans[u])

    if not yes:
        stack.remove(A[u])


dfs(0)

for yes in ans:
    print("Yes" if yes else "No")
