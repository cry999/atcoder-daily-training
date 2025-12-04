N, Q = map(int, input().split())


class UnionFind:
    def __init__(self, n: int):
        self.parent = [None]*n
        self.size = [1]*n

    def find(self, u: int) -> int:
        if not self.parent[u]:
            return u
        self.parent[u] = self.find(self.parent[u])
        return self.parent[u]

    def union(self, u: int, v: int):
        ru, rv = self.find(u), self.find(v)
        if self.size[ru] < self.size[rv]:
            ru, rv = rv, ru

        self.parent[rv] = ru
        self.size[ru] += self.size[rv]


uf = UnionFind(N)

for _ in range(Q):
    query, *params = map(int, input().split())

    if query == 1:
        u, v = params
        uf.union(u-1, v-1)
    elif query == 2:
        v = params[0]
