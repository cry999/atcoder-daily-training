class UnionFind:
    def __init__(self, n: int):
        self.n = n
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def union(self, x: int, y: int):
        x, y = self.find(x), self.find(y)
        if x == y:
            return False
        if self.size[x] < self.size[y]:
            x, y = y, x
        self.root[y] = x
        self.size[x] += self.size[y]
        return True

    def same(self, x: int, y: int):
        return self.find(x) == self.find(y)


N, M, Q = map(int, input().split())
# 重みでソートしておく。
edges = []
for _ in range(M):
    u, v, w = map(int, input().split())
    edges.append((w, u, v))

edges.sort()

queries = []
for i in range(Q):
    u, v, w = map(int, input().split())
    queries.append((w, u, v, i))

queries.sort(reverse=True)

uf = UnionFind(N + 1)

ans = [False] * Q
for w, u, v in edges:
    while queries and queries[-1][0] < w:
        # 先にクエリの辺が組み込めるかを確認する。
        _, qu, qv, qi = queries.pop()
        ans[qi] = not uf.same(qu, qv)

    uf.union(u, v)

for a in ans:
    print("Yes" if a else "No")
