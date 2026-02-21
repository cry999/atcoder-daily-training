import sys

sys.setrecursionlimit(10**7)


N, M = map(int, input().split())

g = [[] for _ in range(N + 1)]

for _ in range(M):
    u, v = map(int, input().split())

    g[u].append(v)

# dfs で訪問済みの頂点。
# dfs を複数回実施する過程で訪問済みフラグは継承される。
visited = [False] * (N + 1)
cnt_visited = 0

# 頂点 1 から到達可能な頂点
reachable = [False] * (N + 1)
cnt_reachable = 0


def dfs(u: int, limit: int):
    global cnt_visited, cnt_reachable
    visited[u] = True
    cnt_visited += 1

    for v in g[u]:
        if not visited[v] and v <= limit:
            # まだ訪問しておらず、limit 以下の番号である頂点であれば訪問する。
            dfs(v, limit)

        if not reachable[v]:
            # Gi から訪問可能な頂点であることを記録する。
            # これには Gi に含まれない頂点も含まれる。
            # 到達可能性だけをマークしており、実際に訪問するかは別。
            cnt_reachable += 1
            reachable[v] = True

    return


reachable[1] = True
cnt_reachable += 1
for i in range(N):
    i += 1

    if reachable[i]:
        # i から到達可能な頂点を全て調査する。
        dfs(i, i)

    if cnt_visited == i:
        print(cnt_reachable - cnt_visited)
    else:
        print(-1)
