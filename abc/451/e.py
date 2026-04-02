import sys

input = sys.stdin.readline
sys.setrecursionlimit(10**7)


class UnionFind:
    def __init__(self, n: int):
        self.n = n
        self.root = [i for i in range(n)]
        self.size = [1] * n

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

    def same(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


N = int(input())

s = []
A = [[0] * N for _ in range(N)]
for i in range(N - 1):
    (*a,) = map(int, input().split())
    for di, w in enumerate(a):
        j = i + di + 1

        A[i][j] = A[j][i] = w
        s.append((w, i, j))
s.sort()
g = [[] for _ in range(N)]

uf = UnionFind(N)
for w, i, j in s:
    if uf.same(i, j):
        continue
    uf.union(i, j)

    g[i].append((j, w))
    g[j].append((i, w))

for i in range(N):
    dist = [-1] * N
    dist[i] = 0
    stack = [i]

    while stack:
        v = stack.pop()
        dv = dist[v]

        for u, w in g[v]:
            if dist[u] != -1:
                continue
            dist[u] = dv + w
            stack.append(u)

    for j in range(i + 1, N):
        if dist[j] != A[i][j]:
            print("No")
            exit()
print("Yes")
