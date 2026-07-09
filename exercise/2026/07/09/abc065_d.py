# >>> atcoder-stat >>>
# started_at  = 2026-07-09T15:54:55+09:00
# solved_at   = 2026-07-09T16:03:03+09:00
# duration_ms = 488853
# target_ms   = 900000
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
        self.parent = [None] * n
        self.size = [1] * n

    def find(self, u: int) -> int:
        while self.parent[u] is not None:
            u = self.parent[u]
        return u

    def merge(self, u: int, v: int):
        ru, rv = self.find(u), self.find(v)
        if ru == rv:
            return False
        if self.size[ru] < self.size[rv]:
            ru, rv = rv, ru

        self.parent[rv] = ru
        self.size[ru] += self.size[rv]
        return True


N = int(input())
cities = []
for i in range(N):
    x, y = map(int, input().split())
    cities.append((x, y, i))

# コストは min(|x1-x2|, |y1-y2|) で定義されるので、辺の候補は x, y のお隣さん
# だけを考えれば良い。それぞれでソートして考える。
edges = []

# x でソート
cities.sort(key=lambda c: c[0])
for i in range(N - 1):
    x1, _, i1 = cities[i]
    x2, _, i2 = cities[i + 1]
    edges.append((x2 - x1, i1, i2))

# y でソート
cities.sort(key=lambda c: c[1])
for i in range(N - 1):
    _, y1, i1 = cities[i]
    _, y2, i2 = cities[i + 1]
    edges.append((y2 - y1, i1, i2))

edges.sort()
uf = UnionFind(N)
ans = 0
for cost, i, j in edges:
    if uf.merge(i, j):
        ans += cost
print(ans)
