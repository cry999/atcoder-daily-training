N = int(input())
sx, sy, tx, ty = map(int, input().split())
circles = [tuple(map(int, input().split())) for _ in range(N)]


class UnionFind:
    def __init__(self, n: int) -> "UnionFind":
        self.root = [i for i in range(n)]
        self.size = [1] * n
        return

    def union(self, u: int, v: int):
        u, v = self.find(u), self.find(v)
        if u == v:
            return
        if self.size[u] < self.size[v]:
            u, v = v, u

        self.size[u] += self.size[v]
        self.root[v] = u
        return

    def find(self, u: int) -> int:
        if self.root[u] == u:
            return u
        self.root[u] = self.find(self.root[u])
        return self.root[u]


uf = UnionFind(N)
for i in range(N):
    xi, yi, ri = circles[i]
    for j in range(N):
        xj, yj, rj = circles[j]
        d = (xi - xj) ** 2 + (yi - yj) ** 2
        if (ri - rj) ** 2 <= d <= (ri + rj) ** 2:
            uf.union(i, j)

s_located = []
t_located = []
for i in range(N):
    xi, yi, ri = circles[i]
    if (sx - xi) ** 2 + (sy - yi) ** 2 == ri**2:
        s_located.append(i)
    if (tx - xi) ** 2 + (ty - yi) ** 2 == ri**2:
        t_located.append(i)

for si in s_located:
    for ti in t_located:
        if uf.find(si) == uf.find(ti):
            print("Yes")
            break
    else:
        continue
    break
else:
    print("No")
