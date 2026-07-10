# >>> atcoder-stat >>>
# started_at  = 2026-07-10T15:40:25+09:00
# solved_at   = 2026-07-10T15:43:39+09:00
# duration_ms = 194624
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
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
edges = []

for _ in range(M):
    a, b = map(int, input().split())
    edges.append((a, b))

bridge = 0
for i in range(M):
    uf = UnionFind(N + 1)
    roots = N
    for j in range(M):
        if i == j:
            continue
        a, b = edges[j]
        if uf.merge(a, b):
            roots -= 1
    if roots > 1:
        bridge += 1
print(bridge)
