class UnionFind:
    def __init__(self, n: int) -> None:
        self.size = [1] * n
        self.par = [None] * n

    def unite(self, u: int, v: int):
        ru, rv = self.root(u), self.root(v)  # root_u, root_v
        if ru == rv:
            return
        if self.size[ru] < self.size[rv]:
            self.par[ru] = rv
            self.size[rv] += self.size[ru]
        else:
            self.par[rv] = ru
            self.size[ru] += self.size[rv]

    def root(self, u: int) -> int:
        while self.par[u] is not None:
            u = self.par[u]
        return u

    def same(self, u: int, v: int) -> bool:
        return self.root(u) == self.root(v)


N, Q = map(int, input().split())
uf = UnionFind(N+1)

for _ in range(Q):
    q, u, v = map(int, input().split())
    if q == 1:
        uf.unite(u, v)
    else:  # q == 2
        print('Yes' if uf.same(u, v) else 'No')
