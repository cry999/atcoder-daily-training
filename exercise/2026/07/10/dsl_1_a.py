class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def same(self, x: int, y: int):
        return self.find(x) == self.find(y)

    def merge(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]
        return True


N, Q = map(int, input().split())
uf = UnionFind(N)

for _ in range(Q):
    com, x, y = map(int, input().split())
    if com == 0:
        uf.merge(x, y)
    else:
        print(int(uf.same(x, y)))
