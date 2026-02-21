class UnionFind:
    def __init__(self, n: int) -> "UnionFind":
        self.root = [i for i in range(n)]
        self.size = [1] * n

    def find(self, x: int) -> int:
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def same(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)

    def union(self, x: int, y: int):
        x, y = self.find(x), self.find(y)
        if x == y:
            return
        if self.size[x] < self.size[y]:
            x, y = y, x

        self.root[y] = x
        self.size[x] += self.size[y]

        return


N, K, Q = map(int, input().split())
(*A,) = map(int, input().split())

union_find = UnionFind(N)

for i in range(N - 1):
    if abs(A[i] - A[i + 1]) <= K:
        union_find.union(i, i + 1)


for _ in range(Q):
    l, r = map(int, input().split())
    if union_find.same(l - 1, r - 1):
        print("Yes")
    else:
        print("No")
