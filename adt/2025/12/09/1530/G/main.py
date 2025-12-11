import bisect


class UnionFind():
    def __init__(self, n: int):
        self._size = [1] * n
        self._parent = [-1] * n

    def find(self, x: int) -> int:
        if self._parent[x] < 0:
            return x
        self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: int, y: int):
        x, y = self.find(x), self.find(y)
        if self._size[x] < self._size[y]:
            x, y = y, x
        self._parent[y] = x
        self._size[x] += self._size[y]

    def size(self, x: int) -> int:
        return self._size[self.find(x)]


N = int(input())

edges = []
for _ in range(N-1):
    u, v, w = map(int, input().split())
    bisect.insort(edges, (w, u-1, v-1))


uf = UnionFind(N)
cnt = 0
for w, u, v in edges:
    cnt += uf.size(u) * uf.size(v) * w
    uf.union(u, v)

print(cnt)
