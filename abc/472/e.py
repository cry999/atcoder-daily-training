import sys

sys.setrecursionlimit(10**6)
input = sys.stdin.readline


T = int(input())

for _ in range(T):
    N, M = map(int, input().split())
    g = [[] for _ in range(N)]

    for _ in range(M):
        a, b = map(int, input().split())
        a, b = a - 1, b - 1
        g[a].append(b)
        g[b].append(a)

    seen = [False] * N
    finished = [False] * N
    parent = [-1] * N
    depth = [0] * N

    ans = []

    def dfs(u: int, p: int):
        seen[u] = True

        for v in g[u]:
            if v == p:
                continue
            if not seen[v]:
                parent[v] = u
                depth[v] = depth[u] + 1

                if dfs(v, u):
                    return True
            elif not finished[u] and depth[u] % 2 == depth[v] % 2:
                cursor = u
                while cursor != v:
                    ans.append(cursor)
                    cursor = parent[cursor]

                ans.append(v)
                return True

        finished[u] = True
        return False

    if dfs(0, -1):
        print(len(ans))
        print(*[x + 1 for x in ans])
    else:
        print(-1)
