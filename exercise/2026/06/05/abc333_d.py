import sys

input = sys.stdin.readline

N = int(input())
g = [[] for _ in range(N)]

for _ in range(N - 1):
    u, v = map(int, input().split())
    u -= 1
    v -= 1

    g[u].append(v)
    g[v].append(u)


d = [0] * N
stack = [(v, v, 0) for v in g[0]]
while stack:
    u, r, p = stack.pop()
    d[r] += 1

    for v in g[u]:
        if v != p:
            stack.append((v, r, u))


print(sum(sorted(d[v] for v in g[0])[:-1]) + 1)
