N, Q = map(int, input().split())


class WeightenUnionFind:
    def __init__(self, n: int):
        self.root = [i for i in range(n)]
        self.size = [1] * n
        self.diff_weight = [0] * n  # 親との重み差

    def find(self, u: int) -> int:
        if self.root[u] != u:
            # 経路圧縮

            # 先に親の重みを計算させる
            r = self.find(self.root[u])
            # 親を更新する前に直接の親の重みを加算
            self.diff_weight[u] += self.diff_weight[self.root[u]]
            self.root[u] = r
        return self.root[u]

    def issame(self, u: int, v: int) -> bool:
        return self.find(u) == self.find(v)

    def weight(self, u: int) -> int:
        self.find(u)  # 根までの重みを計算
        return self.diff_weight[u]

    def diff(self, u: int, v: int) -> int:
        return self.weight(v) - self.weight(u)

    def union(self, u: int, v: int, w: int):
        """v - u = w となるように merge する"""
        w += self.weight(u)
        w -= self.weight(v)

        u, v = self.find(u), self.find(v)
        if u == v:
            return

        if self.size[u] < self.size[v]:
            u, v, w = v, u, -w

        self.size[u] += self.size[v]
        self.root[v] = u
        self.diff_weight[v] = w
        return


wuf = WeightenUnionFind(N + 1)
ans = []
for i in range(Q):
    a, b, d = map(int, input().split())
    if wuf.issame(a, b):
        if wuf.diff(b, a) == d:
            ans.append(i + 1)
    else:
        ans.append(i + 1)
        wuf.union(b, a, d)
print(*ans)
