import heapq


class UnionFind:
    def __init__(self, n: int):
        self.root = [-1] * n
        self.size = [1] * n

    def union(self, u: int, v: int):
        u, v = self.find(u), self.find(v)
        if u == v:
            return
        if self.size[u] < self.size[v]:
            u, v = v, u
        self.root[v] = u
        self.size[u] += self.size[v]

    def find(self, u: int) -> int:
        r = self.root[u]
        if r == -1:
            return u
        self.root[u] = self.find(r)
        return self.root[u]

    def same(self, u: int, v: int) -> bool:
        return self.find(u) == self.find(v)


# クエリ込みで最小全域木を作ることを試みる。
# ただし、クエリの辺は実際に採用するのではなく dry-run だけ実施する。
N, M, Q = map(int, input().split())
edges = []

for _ in range(M):
    a, b, c = map(int, input().split())
    heapq.heappush(edges, (c, a, b, float('inf')))

ans = [''] * Q
for q in range(Q):
    u, v, w = map(int, input().split())
    heapq.heappush(edges, (w, u, v, q))

uf = UnionFind(N+1)
# 最小全域木を完成させる必要はなく、クエリに全部答えたら終了する。
answered = 0
while edges and answered < Q:
    _, u, v, q = heapq.heappop(edges)
    if q == float('inf'):
        uf.union(u, v)
    else:
        answered += 1
        ans[q] = 'No' if uf.same(u, v) else 'Yes'

print('\n'.join(ans))
