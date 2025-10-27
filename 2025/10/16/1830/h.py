class UnionFind:
    def __init__(self, n: int):
        self._parent = [None] * n
        self._size = [1] * n

    def root(self, u: int) -> int:
        if self._parent[u] is None:
            return u
        self._parent[u] = self.root(self._parent[u])
        return self._parent[u]

    def same(self, u: int, v: int) -> bool:
        return self.root(u) == self.root(v)

    def unite(self, u: int, v: int):
        ru, rv = self.root(u), self.root(v)
        if ru == rv:
            return

        if self._size[ru] < self._size[rv]:
            ru, rv = rv, ru

        self._parent[rv] = ru
        self._size[ru] += self._size[rv]


N, M = map(int, input().split())
*A, = map(int, input().split())
A = [0]+A

g = [[] for _ in range(max(A)+1)]
uf = UnionFind(N+1)

for _ in range(M):
    u, v = map(int, input().split())
    if A[u] > A[v]:
        u, v = v, u
    # 小さい方から大きい方へのみ辺を張る
    if A[u] == A[v]:
        uf.unite(u, v)
    else:
        g[A[u]].append((u, v))

# print(g)
# dp[v] := 頂点 1 から頂点 v まで到達する際の最高スコア
dp = [-float('inf')] * (N+1)
# dp[1] := 頂点 1 から頂点 1 まで到達する際の最高スコア = 1
dp[uf.root(1)] = 1

# A の値が小さい方から順に見ていく
# A の値が大きいものの後に A の値が小さいもので最高スコアが更新されることはない
for a in sorted(A):
    # print('=== a:', a, '===')
    for u, v in g[a]:
        ru, rv = uf.root(u), uf.root(v)
        # print(u, v, ru, rv, dp[rv], dp[ru])
        dp[rv] = max(dp[rv], dp[ru]+1)

# print(dp)
print(max(0, dp[uf.root(N)]))
