import sys

sys.setrecursionlimit(10**6)


class Edge:
    def __init__(self, to: int, cap: int, rev: int):
        self.to = to
        self.cap = cap
        self.rev = rev

    def update_cap(self, diff: int):
        self.cap += diff

    def __repr__(self):
        return f'<{self.to=}, {self.cap=}, {self.rev=}>'


class MaximumFlow:
    def __init__(self, nodes: int):
        self.edges: list[Edge] = [[] for _ in range(nodes+1)]
        self.used = [False] * (nodes+1)

    def add_edge(self, u: int, v: int, cap: int):
        '''u -> v: cap'''
        forward = Edge(v, cap, len(self.edges[v]))
        backward = Edge(u, 0, len(self.edges[u]))
        self.edges[u].append(forward)
        self.edges[v].append(backward)

    def flow(self, start: int, goal: int) -> float:
        for i, *_ in enumerate(self.used):
            self.used[i] = False
        return self._dfs_flow(start, goal, float('inf'))

    def _dfs_flow(self, start: int, goal: int, upper: float) -> float:
        if start == goal:
            return upper
        self.used[start] = True
        for i, e in enumerate(self.edges[start]):
            if not e.cap:
                continue
            if self.used[e.to]:
                continue
            f = self._dfs_flow(e.to, goal, min(upper, e.cap))
            if f:
                self.edges[start][i].update_cap(-f)
                self.edges[e.to][e.rev].update_cap(+f)
                return f  # 流せた量を返す
        return 0  # 流せなかったので 0

    def max_flow(self, start: int, goal: int) -> float:
        total = 0
        while True:
            f = self.flow(start, goal)
            if not f:
                break
            total += f
        return total

    def __repr__(self):
        return '\n'.join(
            f'{u} -> {es}' for u, es in enumerate(self.edges) if u > 0
        )


N, M = map(int, input().split())

S, T = N, N+1
ff = MaximumFlow(T+1)

offset = 0
for i, p in enumerate(map(int, input().split())):
    if p >= 0:
        offset += p
        ff.add_edge(S, i, p)
    else:
        ff.add_edge(i, T, -p)

for _ in range(M):
    a, b = map(int, input().split())
    # print(a, b)
    ff.add_edge(a-1, b-1, float('inf'))

# print(ff)
print(offset - ff.max_flow(S, T))
