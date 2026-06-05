class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n
        self.edge = [0] * n
        return

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
        self.root[ry] = self.root[rx]
        self.size[rx] += self.size[ry]
        self.edge[rx] += self.edge[ry] + 1
        return True


N, M = map(int, input().split())
uf = UnionFind(N + 1)

for _ in range(M):
    a, b = map(int, input().split())
    uf.union(a, b)

used = [False] * (N + 1)

ans = 0
for i in range(1, N + 1):
    r = uf.find(i)
    if used[r]:
        continue
    used[r] = True

    ans += uf.size[r] * (uf.size[r] - 1) // 2 - uf.edge[r]

print(ans)
