import heapq


class UnionFind:
    def __init__(self, n: int):
        self.parent = [None] * n
        self.size = [1] * n

    def unite(self, u: int, v: int):
        ru, rv = self.root(u), self.root(v)
        if ru == rv:
            return
        if self.size[ru] < self.size[rv]:  # ru をサイズの大きいノードにする
            ru, rv = rv, ru
        self.parent[rv] = ru
        self.size[ru] += self.size[rv]

    def root(self, u: int) -> int:
        while self.parent[u] is not None:
            u = self.parent[u]
        return u

    def same(self, u: int, v: int) -> bool:
        return self.root(u) == self.root(v)


N, M = map(int, input().split())
edges = []
for _ in range(M):
    a, b, c = map(int, input().split())
    heapq.heappush(edges, (c, a, b))

uf = UnionFind(N+1)
total = 0
while edges:
    c, a, b = heapq.heappop(edges)
    if uf.same(a, b):
        continue
    total += c
    uf.unite(a, b)

print(total)
