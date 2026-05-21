import sys

sys.setrecursionlimit(10**7)
input = sys.stdin.readline

N = int(input())
(*A,) = map(int, input().split())

g = [[] for _ in range(N)]

for _ in range(N - 1):
    u, v = map(lambda x: int(x) - 1, input().split())
    g[u].append(v)
    g[v].append(u)

appeared = set()
ans = [False] * N


def dfs(u: int, ok: bool = False, p: int = -1):
    # print(f"dfs({u}, {p})")
    # print(f"  {appeared=}")
    if A[u] in appeared:
        ans[u] = True
        should_remove = False
    else:
        appeared.add(A[u])
        should_remove = True

    if ok:
        ans[u] = True

    for v in g[u]:
        if v == p:
            continue

        dfs(v, ok or ans[u], u)

    if should_remove:
        appeared.remove(A[u])


dfs(0)
for a in ans:
    print("Yes" if a else "No")
