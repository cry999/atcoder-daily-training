# >>> atcoder-stat >>>
# started_at  = 2026-09-19T10:51:38+09:00
# solved_at   = 2026-09-19T11:07:08+09:00
# duration_ms = 930339
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from itertools import combinations


class UnionFind:
    def __init__(self, n: int):
        self.n = n
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        assert 0 <= x < self.n

        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def union(self, x: int, y: int):
        assert 0 <= x < self.n
        assert 0 <= y < self.n

        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.root[ry] = rx
        self.size[rx] += self.size[ry]
        return True

    def root_size(self, x: int):
        assert 0 <= x < self.n

        return self.size[self.find(x)]


N, M, K = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]

ans = K
for s in combinations(range(M), N - 1):
    weight = 0
    uf = UnionFind(N)

    for i in s:
        u, v, w = edges[i]
        weight += w

        if not uf.union(u - 1, v - 1):
            break
    else:
        ans = min(ans, weight % K)

print(ans)
