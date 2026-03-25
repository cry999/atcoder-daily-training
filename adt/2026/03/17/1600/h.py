N, M = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]
rest_edges = []


class UnionFind:
    def __init__(self, n: int):
        self.n = n
        self.root = [i for i in range(n)]
        self.size = [1] * n

    def find(self, x: int) -> int:
        r = self.root[x]
        if r != x:
            self.root[x] = self.find(r)
        return self.root[x]

    def union(self, x: int, y: int):
        x, y = self.find(x), self.find(y)
        if x == y:
            return
        if self.size[x] < self.size[y]:
            x, y = y, x

        self.root[y] = x
        self.size[x] += self.size[y]

        return

    def same(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


# サーバ同士が繋がっているかを管理する UnionFind
uf = UnionFind(N + 1)

for i, (u, v) in enumerate(edges):
    if uf.same(u, v):
        rest_edges.append((i, u, v))
        continue

    uf.union(u, v)

islands = set()
for i in range(1, N + 1):
    islands.add(uf.find(i))

ans = []
for i, u, v in rest_edges:
    while islands:
        p = islands.pop()
        if uf.same(p, u):
            continue

        uf.union(p, u)
        ans.append((i, v, p))
        break

    islands.add(uf.find(u))

print(len(ans))
for i, u, v in ans:
    print(i + 1, u, v)
