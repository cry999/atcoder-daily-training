import sys

sys.setrecursionlimit(10**6)


class Edge:
    def __init__(self, to: int, cap: int, rev):
        self.to, self.cap, self.rev = to, cap, rev


class FordFulkerson:
    def __init__(self, n: int):
        self.g = [[] for _ in range(n+1)]
        self.used = [False] * (n+1)

    def add_edge(self, u: int, v: int, cap: int):
        e = Edge(v, cap, None)
        r = Edge(u, 0, e)
        e.rev = r

        self.g[u].append(e)
        self.g[v].append(r)

    def flow(self, start: int, goal: int) -> float:
        for i, _ in enumerate(self.used):
            self.used[i] = False
        return self._flow(start, goal, float('inf'))

    def _flow(self, start: int, goal: int, upper: float) -> float:
        if start == goal:
            return upper
        self.used[start] = True
        for e in self.g[start]:
            if not e.cap:
                continue
            if self.used[e.to]:
                continue
            f = self._flow(e.to, goal, min(upper, e.cap))
            if f:
                e.cap -= f
                e.rev.cap += f
                return f

        return 0

    def max_flow(self, start: int, goal: int) -> float:
        total = 0
        while True:
            f = self.flow(start, goal)
            if not f:
                break
            total += f
        return total


N, M = map(int, input().split())
S = 0
G = 1+N+24
ff = FordFulkerson(G)
for i in range(N):
    ff.add_edge(S, i+1, 10)
for i in range(N):
    C = input()
    for h, c in enumerate(C):
        if c == '0':
            continue
        ff.add_edge(i+1, N+h+1, 1)
for h in range(24):
    ff.add_edge(N+h+1, G, M)

print('Yes' if ff.max_flow(S, G) == M*24 else 'No')
