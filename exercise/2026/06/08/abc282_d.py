from collections import deque, defaultdict


class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n
        self.edge = [0] * n

    def find(self, x: int):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            self.edge[rx] += 1
            return False
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.root[ry] = rx
        self.size[rx] += self.size[ry]
        self.edge[rx] += self.edge[ry] + 1
        return True


WHITE = 0
BLACK = 1

N, M = map(int, input().split())
g = [set() for _ in range(N)]

uf = UnionFind(N)

for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].add(v)
    g[v].add(u)

    uf.union(u, v)

roots = set()
for i in range(N):
    roots.add(uf.find(i))

color = [-1] * N


def check_bipartite():
    q = deque()
    for r in roots:
        color[r] = WHITE
        q.append((r, WHITE))

    while q:
        u, c = q.popleft()

        for v in g[u]:
            if color[v] == c:
                return False
            if color[v] == 1 - c:
                continue
            color[v] = 1 - c
            q.append((v, 1 - c))
    return True


roots = list(roots)
if check_bipartite():
    # 連結成分が 2 つある場合は、それぞれの連結成分が二部グラフであれば
    # 2 つの連結成分の任意の頂点を結んで良い。
    white = defaultdict(int)

    for i in range(N):
        if color[i] == WHITE:
            white[uf.find(i)] += 1

    ans = 0
    s = sum(uf.size[r] for r in roots)
    for r in roots:
        s -= uf.size[r]
        ans += s * uf.size[r]

        # 連結成分が 1 つの場合は、そもそもその連結成分が二部グラフでないといけない。
        # その上で、繋がっていない、異なる色の頂点を結びつけられる。
        black = uf.size[r] - white[r]
        ans += black * white[r] - uf.edge[r]
    print(ans)
else:
    print(0)
