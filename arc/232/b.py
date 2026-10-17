import sys

input = sys.stdin.readline


T = int(input())
for _ in range(T):
    N = int(input())

    cards = []
    g = {}
    for i in range(N):
        a, b = map(int, input().split())
        cards.append(a)
        cards.append(b)
        g.setdefault(a, []).append(2 * i + 1)
        g.setdefault(b, []).append(2 * i)

    start, goal = 0, 2 * 1 + 1

    dist = [-1] * (2 * N)
    dist[start] = 0

    q = [start]
    ans = -1
    for u in q:
        if u == goal:
            ans = dist[u]
            break

        x = cards[u]
        cannot = u ^ 1

        r = []
        for v in g[x]:
            if v == cannot:
                r.append(v)
                continue
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)

        g[x] = r

    print(ans)
