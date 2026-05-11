N, M = map(int, input().split())
edges = []

for _ in range(M):
    a, b, c = map(int, input().split())
    edges.append((c, a, b))


class UnionFind:
    def __init__(self, n: int):
        self.root = [i for i in range(n)]
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


uf = UnionFind(N + 1)
edges.sort()

# 最小全域木を構築する。
score = 0
for c, a, b in edges:
    if uf.union(a, b):
        # 最小全域木に必要なので score には加えない
        pass
    elif c < 0:
        # 最小全域木に必要ないが、コストがマイナスなので木に残しておく
        pass
    else:
        # 削除していいし、プラスなので削除してスコアに加算する
        score += c
print(score)
