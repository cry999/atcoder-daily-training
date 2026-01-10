from collections import defaultdict


N, M, K = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]
edges.sort(key=lambda x: x[-1])
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())


class UnionFind:
    def __init__(self, n: int):
        self.size = [1] * n
        self.parent = [i for i in range(n)]
        return

    def root(self, x: int) -> int:
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.root(p)
        return self.parent[x]

    def union(self, u: int, v: int):
        u, v = self.root(u), self.root(v)
        if u == v:
            return
        if self.size[u] < self.size[v]:
            u, v = v, u
        self.parent[v] = u
        self.size[u] += self.size[v]
        return

    def same(self, u: int, v: int) -> bool:
        return self.root(u) == self.root(v)


hist_a = defaultdict(int)
hist_b = defaultdict(int)

for k in range(K):
    hist_a[A[k]] += 1
    hist_b[B[k]] += 1

uf = UnionFind(N + 1)
ans = 0
for u, v, w in edges:
    ru, rv = uf.root(u), uf.root(v)
    if ru == rv:
        continue
    uf.union(ru, rv)
    if ru != uf.root(ru):
        # u が v の下にマージされた場合
        # u が親になるようにする。
        ru, rv = rv, ru

    hist_a[ru] += hist_a[rv]
    hist_b[ru] += hist_b[rv]
    hist_a[rv] = hist_b[rv] = 0

    if hist_a[ru] and hist_b[ru]:
        d = min(hist_a[ru], hist_b[ru])
        hist_a[ru] -= d
        hist_b[ru] -= d
        ans += w * d


print(ans)
