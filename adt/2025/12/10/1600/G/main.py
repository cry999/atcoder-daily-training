import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


class UnionFind:
    def __init__(self, n: int) -> 'UnionFind':
        self.parent = [-1]*n
        self.size = [1]*n

    def find(self, x: int) -> int:
        p = self.parent[x]
        if p == -1:
            return x
        self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, u: int, v: int):
        u, v = self.find(u), self.find(v)
        if u == v:
            return
        if self.size[u] < self.size[v]:
            u, v = v, u
        self.size[u] += self.size[v]
        self.parent[v] = u


N, M = map(int, input().split())
uf = UnionFind(N)
g = [[] for _ in range(N)]

for _ in range(M):
    u, v = map(int, input().split())
    u, v = u-1, v-1

    g[u].append(v)
    g[v].append(u)

    uf.union(u, v)

# union find で連結成分がわかる。

# 各ノードを回りながら
# 1. 連結成分のサイズを求める
# 2. 各成分が二部グラフであるかを確認する

# visited[i] = -1: 未訪問 / 0: 色 0 / 1: 色 1
visited = [-1] * N


def is_bipartie(u: int) -> tuple[int, int, bool]:
    q = [(u, 0)]
    b, w = 0, 0  # bloack = 0, white = 1
    while q:
        v, c = q.pop()
        debug(f'{v=}, {c=}')
        if visited[v] == c:
            debug('  visited continue')
            continue
        if visited[v] == 1-c:
            debug('  visited BREAK')
            return -1, -1, False
        # not visited
        visited[v] = c
        b, w = b+(c == 0), w+(c == 1)
        for nv in g[v]:
            debug(f'  {nv=}')
            if visited[nv] == 1-c:
                debug('    next node visited continue')
                continue
            if visited[nv] == c:
                debug(f'    next node visited BREAK {visited[nv]=}, {1-c=}')
                return -1, -1, False
            q.append((nv, 1-c))
    return b, w, True


inv = 0  # 追加しても 2 部グラフにはならない辺の数
for u in range(N):
    if visited[u] != -1:
        continue
    b, w, ok = is_bipartie(u)
    if not ok:
        inv = N*(N-1)//2 - M
        debug('not is_bipartie')
        break
    # 同一連結成分ないの同一グループのノード同士だけ辺を追加する価値がない。
    inv += b*(b-1)//2 + w*(w-1)//2


print(N*(N-1)//2 - M - inv)
