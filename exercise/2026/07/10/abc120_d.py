# >>> atcoder-stat >>>
# started_at  = 2026-07-10T15:44:01+09:00
# solved_at   = 2026-07-10T15:51:07+09:00
# duration_ms = 426710
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def same(self, x: int, y: int):
        return self.find(x) == self.find(y)

    def size_of(self, x: int):
        return self.size[self.find(x)]

    def merge(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]
        return True


N, M = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]

uf = UnionFind(N + 1)
ans = [0] * M
inconvenience = N * (N - 1) // 2

for i in range(M - 1, -1, -1):
    ans[i] = inconvenience
    a, b = edges[i]
    if not uf.same(a, b):
        inconvenience -= uf.size_of(a) * uf.size_of(b)
        uf.merge(a, b)
print("\n".join(map(str, ans)))
