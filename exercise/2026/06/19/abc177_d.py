N, M = map(int, input().split())


class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def size_of(self, x: int):
        return self.size[self.find(x)]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.root[rx] = ry
        self.size[ry] += self.size[rx]
        return True


uf = UnionFind(N + 1)
ans = 1
for _ in range(M):
    a, b = map(int, input().split())

    if uf.union(a, b):
        ans = max(uf.size_of(a), ans)
print(ans)
