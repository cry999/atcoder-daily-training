import sys

sys.setrecursionlimit(10**7)


N = int(input())
graph: list[list[int]] = [[] for _ in range(N)]

for i in range(N):
    c, *p = map(int, input().split())
    graph[i].extend(u-1 for u in p)


visited = [False]*N
ans: list[int] = []


def dfs(u: int):
    global visited, ans
    # print(f'dfs({u=})')

    if visited[u]:
        # print(f'  visited')
        return
    visited[u] = True

    for v in graph[u]:
        # print(f'{u=} -> {v=}')
        if visited[v]:
            # print('  visited')
            continue
        dfs(v)
    if u > 0:
        ans.append(u)
    return

dfs(0)
print(*map(lambda x: x+1, ans))
