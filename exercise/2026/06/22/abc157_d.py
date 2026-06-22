class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def same(self, x: int, y: int):
        return self.find(x) == self.find(y)

    def size_of(self, x: int):
        return self.size[self.find(x)]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.root[ry] = rx
        self.size[rx] += self.size[ry]
        return True


N, M, K = map(int, input().split())
# 直接の友達
f = [[] for _ in range(N)]
# ブロック
b = [set() for _ in range(N)]

# 友達関係
uf = UnionFind(N)

for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    f[u].append(v)
    f[v].append(u)
    uf.union(u, v)

# 友達関係から、直接の友達を除く
# NOTE: -1 は UnionFind の自分自身を除くため。
ans = [uf.size_of(i) - 1 - len(f[i]) for i in range(N)]

for _ in range(K):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    # 友達関係にないブロック関係は今回関係ない
    if uf.same(u, v):
        ans[u] -= 1
        ans[v] -= 1

print(*ans)
