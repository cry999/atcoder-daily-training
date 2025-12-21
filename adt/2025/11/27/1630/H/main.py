import sys


sys.setrecursionlimit(10**7)


N, M = map(int, input().split())

g = [[] for _ in range(N+1)]
input_edges = [0] * (N+1)
for _ in range(M):
    x, y = map(int, input().split())
    g[x].append(y)
    input_edges[y] += 1

root = -1
for i in range(1, N+1):
    # 入力次数が 0 のものを探す。
    # 複数ある場合は失敗。
    if input_edges[i] != 0:
        continue
    if root != -1:
        print('No')
        exit()
    root = i

if root == -1:
    # 見つからず
    print('No')
    exit()

# DFS で N でたどりづけるルートを探す。
ans = [-1] * (N+1)


def dfs(v: int) -> int:
    if ans[v] != -1:
        return ans[v]

    ans[v] = 0
    for nv in g[v]:
        ans[v] = max(ans[v], dfs(nv)+1)
    return ans[v]


ok = dfs(root)
if ok < N-1:
    print('No')
else:
    print('Yes')
    print(*map(lambda x: N-x, ans[1:]))
