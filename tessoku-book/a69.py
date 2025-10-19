import sys


sys.setrecursionlimit(10**6)


class Edge:
    def __init__(self, to: int, cap: int, rev):
        self.to = to
        self.cap = cap
        self.rev = rev

    def __repr__(self) -> str:
        return f'<{self.to=},{self.cap=},{self.rev.to=}>'


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
            f = self._flow(e.to, goal, min(e.cap, upper))
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

    def __repr__(self) -> str:
        return '\n'.join(
            f'{u}: {es}' for u, es in enumerate(self.g)
        )


N = int(input())
S, G = 0, 2*N+1
# 0 -> 2N+1
# start: 0
# 生徒: 1 ~ N
# せき: N+1 ~ 2N
# goal: 2N+1
ff = FordFulkerson(2*N+1)
for i in range(N):
    ff.add_edge(S, i+1, 1)
for i in range(N):
    C = input()
    for j in range(N):
        if C[j] != '#':
            continue
        ff.add_edge(i+1, N+j+1, 1)
for i in range(N):
    ff.add_edge(N+i+1, G, 1)
# print(ff)
print(ff.max_flow(S, G))
