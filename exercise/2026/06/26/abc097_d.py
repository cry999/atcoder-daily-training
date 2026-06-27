N, M = map(int, input().split())

(*P,) = map(int, input().split())


class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.root[ry] = rx
        self.size[rx] += self.size[ry]
        return True

    def same(self, x: int, y: int):
        return self.find(x) == self.find(y)


uf = UnionFind(N + 1)
for _ in range(M):
    x, y = map(int, input().split())
    uf.union(x, y)

ans = sum(uf.same(i + 1, P[i]) for i in range(N))
print(ans)
