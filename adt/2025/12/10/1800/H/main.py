from collections import defaultdict


class UnionFind:
    def __init__(self, n: int):
        self.root = [-1] * n
        self.size = [1] * n

    def find(self, x: int) -> int:
        if self.root[x] < 0:
            return x
        self.root[x] = self.find(self.root[x])
        return self.root[x]

    def union(self, u: int, v: int):
        u, v = self.find(u), self.find(v)
        if u == v:
            return
        if self.size[u] < self.size[v]:
            u, v = v, u
        self.root[v] = u
        self.size[u] += self.size[v]


N, M = map(int, input().split())
uf = UnionFind(N+1)

for _ in range(M):
    u, v = map(int, input().split())
    uf.union(u, v)

K = int(input())
# 「良いグラフ」であるために、どの連結成分同士が繋がっていはいけないかを管理する。
# 連結成分は UnionFind のルートで表現する。
good = defaultdict(set)

for _ in range(K):
    u, v = map(int, input().split())
    ru, rv = uf.find(u), uf.find(v)
    good[ru].add(rv)
    good[rv].add(ru)

Q = int(input())
for _ in range(Q):
    u, v = map(int, input().split())
    ru, rv = uf.find(u), uf.find(v)

    if ru in good and rv in good[ru]:
        print('No')
    else:
        print('Yes')
