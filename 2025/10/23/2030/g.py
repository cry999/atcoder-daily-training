class UnionFind:
    def __init__(self, n: int):
        self.parent = [-1] * n
        self.size = [1] * n

    def find(self, x: int) -> int:
        if self.parent[x] < 0:
            return x
        self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def unite(self, u: int, v: int):
        ru, rv = self.find(u), self.find(v)
        if ru == rv:  # already united
            return

        if self.size[ru] < self.size[rv]:
            ru, rv = rv, ru

        self.parent[rv] = ru
        self.size[ru] += self.size[rv]

    def count(self) -> int:
        return sum(p < 0 for p in self.parent)

    def roots(self) -> list[int]:
        return [i for i, p in enumerate(self.parent) if p < 0]


N, M = map(int, input().split())

g = [[] for _ in range(N)]
uf = UnionFind(N)

for _ in range(M):
    u, v = map(lambda x: int(x)-1, input().split())
    uf.unite(u, v)
    g[u].append(v)
    g[v].append(u)


color = [0] * N


def is_bipartite(u: int) -> bool:
    ''' グラフ g が 2 部グラフであるかを判定する'''
    # color = 0: 塗ってない, 1: 黒, -1: 白
    queue = []
    color[u] = 1
    b, w = 1, 0
    queue.append((u, 1))
    while queue:
        v, c = queue.pop()
        for nv in g[v]:
            if color[nv] == 0:
                # まだ訪れてない。
                # 色は反転させる。
                color[nv] = -c
                if color[nv] > 0:
                    b += 1
                else:
                    w += 1
                queue.append((nv, -c))
            elif color[nv] == c:
                # 隣接するノードが同じ色になっている
                return False
                # return -1, -1
    return True
    # return b, w


roots = uf.roots()
if any(not is_bipartite(r) for r in roots):
    # どちらか一方でも 2 部グラフでなければどれを繋いでも 2 部グラフにはならない。
    print(0)
else:
    # 2 つ以上の連結成分で構成されるなら、以下の条件のいずれかを満たせば繋げることが可能。
    #
    # 1. 別々の連結成分同士の任意のノード
    # 2. 同じ連結成分内の別々の色のノード
    #
    # 逆に、同じ連結成分の同じ色のノードだけは繋げない。
    # つまり、繋げられるペアの総数は、
    #
    # (全ペア) - (各連結成分での同じ色の成分のペアの総和) - M
    #
    # ここで注意すべきは、(同じ色のペア) は (すでに繋がれているペア) とダブらないこと。
    # もしダブっているなら同じ色のペアが繋がっているので 2 部グラフではない。

    bs, ws = [0] * N, [0] * N
    for i in range(N):
        r = uf.find(i)
        bs[r], ws[r] = bs[r] + (color[i] > 0), ws[r] + (color[i] < 0)
    # print(bs, ws, color)
    print(N*(N-1)//2 -
          sum(b*(b-1)//2 for b in bs) -
          sum(w*(w-1)//2 for w in ws) -
          M)
