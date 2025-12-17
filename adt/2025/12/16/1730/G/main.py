class UnionFind:
    def __init__(self, n: int):
        self.root = [-1] * n
        self.size = [1] * n
        self.edge = [0] * n

    def find(self, x: int) -> int:
        r = self.root[x]
        if r == -1:
            return x
        self.root[x] = self.find(r)
        return self.root[x]

    def union(self, u: int, v: int):
        u, v = self.find(u), self.find(v)
        if u == v:
            self.edge[u] += 1
            return
        if self.size[u] < self.size[v]:
            u, v = v, u

        self.root[v] = u
        self.size[u] += self.size[v]
        self.edge[u] += self.edge[v] + 1


N, M = map(int, input().split())
uf = UnionFind(N+1)

for _ in range(M):
    u, v = map(int, input().split())
    uf.union(u, v)

for i in range(N):
    u = i+1

    r = uf.find(u)
    if uf.size[r] != uf.edge[r]:
        print('No')
        break
else:
    print('Yes')
