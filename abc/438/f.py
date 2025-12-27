# 間違い。
# 理解できていないところが多い。
class LowestCommonAncestor:
    def __init__(self, n: int):
        self.graph_size = n
        self.log_size = n.bit_length()
        self.parent = [[-1]*self.graph_size for _ in range(self.log_size)]
        self.depth = [0]*self.graph_size
        self.graph = [[] for _ in range(self.graph_size)]
        self.size = [1]*self.graph_size

    def build(self, root: int = 0) -> None:
        # parent[0] と depth を初期化する
        stack = [(root, -1, 0)]
        visit_order = []
        while stack:
            v, parent, depth = stack.pop()
            visit_order.append(v)
            self.parent[0][v] = parent
            self.depth[v] = depth
            for nv in self.graph[v]:
                if nv == parent:
                    continue
                stack.append((nv, v, depth+1))

        for v in reversed(visit_order):
            p = self.parent[0][v]
            if p >= 0:
                self.size[p] += self.size[v]

        for k in range(self.log_size-1):
            for v in range(self.graph_size):
                if self.parent[k][v] < 0:
                    self.parent[k+1][v] = -1
                else:
                    self.parent[k+1][v] = self.parent[k][self.parent[k][v]]

    def add_edge(self, u: int, v: int) -> None:
        self.graph[u].append(v)
        self.graph[v].append(u)

    def lca(self, u: int, v: int) -> int:
        '''u と v の最小共通祖先を返す'''
        if self.depth[u] > self.depth[v]:
            u, v = v, u
        for k in range(self.log_size):
            if (self.depth[v]-self.depth[u]) & (1 << k):
                v = self.parent[k][v]
            if u == v:
                return u
            for k in range(self.log_size-1, -1, -1):
                if self.parent[k][u] == self.parent[k][v]:
                    continue
                u = self.parent[k][u]
                v = self.parent[k][v]
        return self.parent[0][u]

    def dist(self, x: int, y: int) -> int:
        '''x と y の距離を返す'''
        lca = self.lca(x, y)
        return self.depth[x] + self.depth[y] - 2 * self.depth[lca]

    def is_on_path(self, x: int, y: int, target: int) -> bool:
        '''x から y へのパス上に target が存在するかどうかを確認する
        x == target or y == target の場合も true を返す。
        '''
        return self.dist(x, target) + self.dist(y, target) == self.dist(x, y)

    def kth_ancestor(self, u: int, k: int = 1) -> int:
        '''u の k つ上の祖先を返す'''
        if self.depth[u] < k:
            return -1
        for i in range(self.log_size):
            if (k >> i) & 1:
                u = self.parent[i][u]
        return u

    def count_paths(self, u: int, v: int) -> int:
        '''u と v を結ぶパス'''
        if self.lca(u, v) == v:
            u, v = v, u
        if self.lca(u, v) == u:
            a = self.kth_ancestor(v, self.depth[v]-self.depth[u]-1)
            size_u = self.graph_size - self.size[a]
            size_v = self.size[v]
        else:
            size_u, size_v = self.size[u], self.size[v]
        return size_u * size_v


N = int(input())
lca = LowestCommonAncestor(N)
for _ in range(N-1):
    u, v = map(int, input().split())
    lca.add_edge(u, v)

lca.build()

x, y = 0, 0
ans = 0
# 最初に 0 を含むパスを数えておく。
# 全ての辺から、0 を含むパスを引く。
ans = N*(N+1)//2
for u in lca.graph[0]:
    ans -= lca.size[u]*(lca.size[u]+1)//2

for k in range(1, N):
    if lca.is_on_path(x, y, k):
        pass
    elif lca.is_on_path(x, k, y):
        # 1. x_{k-1} と k を結ぶパスに y_{k-1} が含まれる場合、
        # (x_k, y_k) = (x_{k-1}, k)
        x, y = x, k
    elif lca.is_on_path(y, k, x):
        # 1. y_{k-1} と k を結ぶパスに x_{k-1} が含まれる場合、
        # (x_k, y_k) = (k, y_{k-1})
        x, y = k, y
    else:
        break
    ans += lca.count_paths(x, y)

print(ans)
