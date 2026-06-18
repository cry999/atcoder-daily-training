class UnionFind:
    def __init__(self, n: int):
        self._root = list(range(n))
        self._size = [1] * n

    def find(self, x: int):
        if self._root[x] != x:
            self._root[x] = self.find(self._root[x])
        return self._root[x]

    def size(self, x: int):
        return self._size[self.find(x)]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        if self._size[rx] < self._size[ry]:
            rx, ry = ry, rx
        self._root[ry] = rx
        self._size[rx] += self._size[ry]
        return True


N = int(input())

edges = []
for _ in range(N - 1):
    u, v, w = map(int, input().split())
    edges.append((w, u, v))

edges.sort()

uf = UnionFind(N + 1)

ans = 0
for w, u, v in edges:
    ans += uf.size(u) * uf.size(v) * w
    uf.union(u, v)

print(ans)
