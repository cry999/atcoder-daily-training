V, E = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(E)]
edges.sort(key=lambda x: x[2])


class UnionFind:
    def __init__(self, n: int):
        self.par = list(range(n))
        self.siz = [1] * n

    def find(self, x: int):
        if self.par[x] != x:
            self.par[x] = self.find(self.par[x])
        return self.par[x]

    def merge(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.siz[rx] < self.siz[ry]:
            rx, ry = ry, rx
        self.par[ry] = rx
        self.siz[rx] += self.siz[ry]
        return True


uf = UnionFind(V)

ans = 0
for u, v, w in edges:
    if uf.merge(u, v):
        ans += w
print(ans)
