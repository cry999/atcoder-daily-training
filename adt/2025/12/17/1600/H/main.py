class UnionFind:
    def __init__(self, n: int):
        self.root = [-1] * n
        self.size = [1] * n

    def find(self, x: int) -> int:
        r = self.root[x]
        if r == -1:
            return x
        self.root[x] = self.find(r)
        return self.root[x]

    def union(self, u: int, v: int):
        u, v = self.find(u), self.find(v)
        if u == v:
            return
        if self.size[u] < self.size[v]:
            u, v = v, u

        self.root[v] = u
        self.size[u] += self.size[v]

    def same(self, u: int, v: int):
        return self.find(u) == self.find(v)


N, M = map(int, input().split())
ABC = [tuple(map(int, input().split())) for _ in range(M)]
ABC.sort(key=lambda x: x[2])
uf = UnionFind(N+1)

score = 0
for A, B, C in ABC:
    if C < 0 or not uf.same(A, B):
        # 負の得点はいらないのでグラフに残しておく。
        # グラフは連結である以外の条件はないので余計な辺を
        # 残していても良い。

        # また、連結成分に必要な場合も辺を追加する。

        uf.union(A, B)
    elif uf.same(A, B):
        # 正の得点で連結グラフに不要なものは特典としてもらう。
        score += C

print(score)
