import sys
from collections import deque

sys.setrecursionlimit(10**7)


N, M = map(int, input().split())

tree = [[] for _ in range(N)]
for _ in range(N - 1):
    x, y = map(lambda x: int(x) - 1, input().split())
    tree[x].append(y)
    tree[y].append(x)

# dp[u] := 頂点 u を根とする部分木について、u を黒く塗る場合の数
# dp[u] = mul(1 + dp[v] for v in tree[u] if v != parent)
dp = [-1 for _ in range(N)]


def dfs(u: int, parent: int) -> int:
    if dp[u] >= 0:
        return dp[u]

    dp[u] = 1
    for v in tree[u]:
        if v == parent:
            continue
        dp[u] *= dfs(v, u) + 1
        dp[u] %= M

    return dp[u]


dfs(0, -1)

ans = [0 for _ in range(N)]
# bfs で各頂点の親の影響を計算
queue = deque([(0, -1, 0)])
while queue:
    u, p, m = queue.popleft()

    parent_term = (m + 1) % M
    ans[u] = (dp[u] * (m + 1)) % M

    k = len(tree[u])
    term = [0] * k
    for i, v in enumerate(tree[u]):
        term[i] = parent_term if v == p else (dp[v] + 1) % M

    prefix = [1] * (k + 1)
    for i in range(k):
        prefix[i + 1] = (prefix[i] * term[i]) % M

    suffix = [1] * (k + 1)
    for i in range(k - 1, -1, -1):
        suffix[i] = (suffix[i + 1] * term[i]) % M

    for i, v in enumerate(tree[u]):
        if v == p:
            continue
        queue.append((v, u, (prefix[i] * suffix[i + 1]) % M))


for a in ans:
    print(a)
