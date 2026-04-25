class UnionFind:
    def __init__(self, n: int):
        self.n = n
        self.root = [i for i in range(n)]
        self.size = [1] * n

    def find(self, x: int) -> int:
        while self.root[x] != x:
            self.root[x] = self.root[self.root[x]]
            x = self.root[x]
        return x

    def union(self, x: int, y: int):
        x, y = self.find(x), self.find(y)
        if x == y:
            return False
        if self.size[x] < self.size[y]:
            x, y = y, x

        self.root[y] = x
        self.size[x] += self.size[y]

        return True


N, M = map(int, input().split())

uf = UnionFind(N)

ans = M
for _ in range(M):
    a, b = map(lambda x: int(x) - 1, input().split())
    if uf.union(a, b):
        ans -= 1

print(ans)
