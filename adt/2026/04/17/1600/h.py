class UnionFind:
    def __init__(self, n: int):
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


N, M = map(int, input().split())
(*A,) = map(int, input().split())

edges = []
for i in range(N):
    for j in range(i + 1, N):
        score = (pow(A[i], A[j], M) + pow(A[j], A[i], M)) % M
        edges.append((score, i, j))
edges.sort(reverse=True)

uf = UnionFind(N)
ans = 0
for score, a, b in edges:
    if uf.union(a, b):
        ans += score

print(ans)
