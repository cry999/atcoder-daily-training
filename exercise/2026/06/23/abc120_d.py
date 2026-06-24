import sys

input = sys.stdin.readline


class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def same(self, x: int, y: int):
        return self.find(x) == self.find(y)

    def size_of(self, x: int):
        return self.size[self.find(x)]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.root[ry] = rx
        self.size[rx] += self.size[ry]
        return True


N, M = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]

uf = UnionFind(N + 1)

ans = []
ans.append(N * (N - 1) // 2)

for _ in range(M):
    a, b = edges.pop()

    if uf.same(a, b):
        ans.append(ans[-1])
        continue

    ans.append(ans[-1] - uf.size_of(a) * uf.size_of(b))
    uf.union(a, b)

ans.reverse()
for a in ans[1:]:
    print(a)
