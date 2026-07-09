from math import sqrt


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


def is_collision(
    xi: float,
    yi: float,
    zi: float,
    ri: float,
    xj: float,
    yj: float,
    zj: float,
    rj: float,
):
    d2 = (xi - xj) ** 2 + (yi - yj) ** 2 + (zi - zj) ** 2
    return d2 <= (ri + rj) ** 2


def dist(
    xi: float,
    yi: float,
    zi: float,
    ri: float,
    xj: float,
    yj: float,
    zj: float,
    rj: float,
):
    d2 = (xi - xj) ** 2 + (yi - yj) ** 2 + (zi - zj) ** 2
    return sqrt(d2) - ri - rj


while True:
    N = int(input())
    if not N:
        break
    cells = [tuple(map(float, input().split())) for _ in range(N)]
    edges = []

    uf = UnionFind(N)
    for i in range(N):
        xi, yi, zi, ri = cells[i]
        for j in range(i + 1, N):
            xj, yj, zj, rj = cells[j]
            if is_collision(xi, yi, zi, ri, xj, yj, zj, rj):
                uf.merge(i, j)
            else:
                edges.append((i, j, dist(xi, yi, zi, ri, xj, yj, zj, rj)))

    edges.sort(key=lambda x: x[2])
    ans = 0
    for i, j, d in edges:
        if uf.merge(i, j):
            ans += d
    print(f"{ans:.3f}")
