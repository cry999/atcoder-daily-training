import sys


sys.setrecursionlimit(10**7)

N = int(input())
g = [[] for _ in range(N + 1)]

for _ in range(N-1):
    u, v = map(int, input().split())
    g[u].append(v)
    g[v].append(u)


def dfs(u: int, depth: int, dist: list[int]):
    stack = [(u, depth)]
    while stack:
        u, depth = stack.pop()
        dist[u] = depth
        for v in g[u]:
            if dist[v] != -1:  # 訪問済み
                continue
            stack.append((v, depth+1))


dist_from_1 = [-1] * (N+1)  # 仮で 1 を根とする
dfs(1, 0, dist_from_1)  # 1 からの距離を計算

# 1 から最も遠い点を直径の端点の 1 つとする
u = N-dist_from_1[::-1].index(max(dist_from_1))
dist_from_u = [-1] * (N+1)  # u を根とする
dfs(u, 0, dist_from_u)  # u からの距離を計算

# u から最も遠い点までの距離が直径
v = N-dist_from_u[::-1].index(max(dist_from_u))
dist_from_v = [-1] * (N+1)  # v を根とする
dfs(v, 0, dist_from_v)  # v からの距離を計算

for i in range(1, N+1):
    if dist_from_u[i] > dist_from_v[i]:
        print(u)
    elif dist_from_u[i] < dist_from_v[i]:
        print(v)
    else:
        print(u if u > v else v)
