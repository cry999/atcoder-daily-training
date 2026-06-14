import sys

input = sys.stdin.readline

N = 1 << 20


class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n
        self.right = list(range(n))

    def find(self, x: int):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def find_right(self, x: int):
        return self.right[self.find(x)]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        right = self.right[ry]

        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.root[ry] = rx
        self.size[rx] += self.size[ry]

        self.right[rx] = right

        return True


uf = UnionFind(N)
A = [-1] * N

Q = int(input())
for _ in range(Q):
    t, x = map(int, input().split())

    if t == 1:
        h = uf.find_right(x % N)
        A[h] = x
        uf.union(h, (h + 1) % N)
    else:
        print(A[x % N])
