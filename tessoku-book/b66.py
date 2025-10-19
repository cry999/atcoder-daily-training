import heapq


class UnionFind:
    def __init__(self, n: int):
        self.size = [1] * n
        self.parent = [None] * n

    def unite(self, u: int, v: int):
        ru, rv = self.root(u), self.root(v)
        if ru == rv:
            return
        if self.size[ru] < self.size[rv]:
            ru, rv = rv, ru

        self.parent[rv] = ru
        self.size[ru] += self.size[rv]

    def root(self, u: int) -> int:
        while self.parent[u] is not None:
            u = self.parent[u]
        return u

    def same(self, u: int, v: int) -> bool:
        return self.root(u) == self.root(v)


MAX_Q = 100_000

N, M = map(int, input().split())
edges = [(-MAX_Q-1, *tuple(map(int, input().split()))) for _ in range(M)]
# print(edges)

Q = int(input())
queries = []

for i in range(Q):
    q, *params = map(int, input().split())
    queries.append((q, *params))
    if q == 1:
        x, *_ = params
        edges[x-1] = (-i, *edges[x-1][1:])

heapq.heapify(edges)

uf = UnionFind(N+1)

while edges:
    i, a, b = heapq.heappop(edges)
    if i == -MAX_Q-1:
        uf.unite(a, b)
        continue
    heapq.heappush(edges, (i, a, b))
    break

ans = []
for q, *params in queries[::-1]:
    if q == 1:
        _, a, b = heapq.heappop(edges)
        uf.unite(a, b)
    else:  # q == 2
        a, b = params
        ans.append('Yes' if uf.same(a, b) else 'No')

print('\n'.join(ans[::-1]))
