class UnionFind:
    def __init__(self, n: int):
        self.root = [i for i in range(n)]
        self.size = [1] * n

    def find(self, x: int) -> int:
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def same(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)

    def union(self, x: int, y: int):
        x, y = self.find(x), self.find(y)
        if x == y:
            return

        if self.size[x] < self.size[y]:
            x, y = y, x

        self.root[y] = x
        self.size[x] += self.size[y]
        return


MOD = 998244353

N, M = map(int, input().split())

edges = [tuple(map(lambda x: int(x) - 1, input().split())) for _ in range(M)]

union_find = UnionFind(N)
components = N

ans = 0

for i, (u, v) in enumerate(reversed(edges)):
    if components == 2 and not union_find.same(u, v):
        ans += pow(2, M - i, MOD)
        ans %= MOD
    else:
        if not union_find.same(u, v):
            components -= 1
        union_find.union(u, v)

print(ans)
