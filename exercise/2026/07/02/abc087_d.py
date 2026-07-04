# >>> atcoder-stat >>>
# started_at  = 2026-07-02T08:33:51+09:00
# solved_at   = 2026-07-02T08:53:08+09:00
# duration_ms = 1157583
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 3
# complexity  = 2
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<


class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n
        self.diff = [0] * n

    def find(self, x: int):
        if self.root[x] == x:
            return x

        r = self.find(self.root[x])
        self.diff[x] += self.diff[self.root[x]]
        self.root[x] = r
        return self.root[x]

    def weight(self, x: int):
        self.find(x)
        return self.diff[x]

    def same(self, x: int, y: int):
        return self.find(x) == self.find(y)

    def merge(self, x: int, y: int, w: int):
        w += self.weight(x) - self.weight(y)
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
            w = -w

        self.size[rx] += self.size[ry]
        self.root[ry] = rx
        self.diff[ry] = w
        return True

    def dist(self, x: int, y: int):
        return abs(self.weight(y) - self.weight(x))


N, M = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]
edges.sort(key=lambda x: x[2])

u = UnionFind(N + 1)

if all(u.merge(l, r, d) or u.dist(l, r) == d for l, r, d in edges):
    print("Yes")
else:
    print("No")
