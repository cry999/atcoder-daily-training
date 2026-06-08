class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n
        self.edge = [0] * n

    def find(self, x: int):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            self.edge[rx] += 1
            return False
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.root[ry] = rx
        self.size[rx] += self.size[ry]
        self.edge[rx] += self.edge[ry] + 1
        return True


N, M = map(int, input().split())

uf = UnionFind(N)

for _ in range(M):
    u, v = map(int, input().split())
    uf.union(u - 1, v - 1)

for u in range(N):
    r = uf.find(u)

    if uf.size[r] != uf.edge[r]:
        print("No")
        break
else:
    print("Yes")
