from sys import setrecursionlimit

setrecursionlimit(10**7)

MOD = 998244353


class UnionFind:
    def __init__(self, n: int):
        self.n = n
        self.root = [i for i in range(self.n)]
        self.size = [1] * self.n

    def find(self, x: int) -> int:
        r = self.root[x]
        if r == x:
            return r
        self.root[x] = self.find(r)
        return self.root[x]

    def union(self, x: int, y: int):
        x, y = self.find(x), self.find(y)
        if x == y:
            return
        if self.size[x] < self.size[y]:
            x, y = y, x

        self.root[y] = x
        self.size[x] += self.size[y]

        return


N = int(input())
E = [0] * N
uf = UnionFind(2 * N - 1)

# トーナメント木を作る。
g = [[] for _ in range(2 * N - 1)]
# チーム i が勝ち残ったことを表現するノードの番号。
# 木を作る過程で必要なだけで、木を作ったら不要。
rounds = [i for i in range(N)]

for i in range(N - 1):
    p, q = map(lambda x: int(x) - 1, input().split())

    r = N + i  # 対戦結果のノード

    fp, fq = uf.find(p), uf.find(q)
    sp, sq = uf.size[fp], uf.size[fq]
    rp, rq = rounds[fp], rounds[fq]

    # rp, rq に残っている勝者が r に進むように木を作る

    g[r].append((rp, sp))
    g[r].append((rq, sq))
    rounds[fp] = rounds[fq] = r

    uf.union(p, q)


def dfs(u: int, prop: int = 0, depth: int = 0) -> None:
    if g[u]:
        # print(" " * depth + f"{u}({prop=})")
        u1, s1 = g[u][0]
        u2, s2 = g[u][1]
        dfs(u1, (prop + s1 * pow(s1 + s2, MOD - 2, MOD)) % MOD, depth + 1)
        dfs(u2, (prop + s2 * pow(s1 + s2, MOD - 2, MOD)) % MOD, depth + 1)
    else:
        # leaf
        # print(" " * depth + f"{u}({prop=}:leaf)")
        E[u] = prop % MOD


dfs(2 * N - 2)
print(*E)
