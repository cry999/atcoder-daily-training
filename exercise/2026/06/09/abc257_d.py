import math
from collections import deque

# X[i, j] = ceil((diff|x| + diff|y|) / S) を計算する。
# 二分探索。~~M 以下の X[i, j] だけで全域木は作れるか？~~
# 有向グラフだ。。。毎回 BFS するか。。。

N = int(input())

jump_boards = [tuple(map(int, input().split())) for _ in range(N)]
g = [[] for _ in range(N)]

for i in range(N):
    x1, y1, p1 = jump_boards[i]
    for j in range(i + 1, N):
        x2, y2, p2 = jump_boards[j]

        d = abs(x1 - x2) + abs(y1 - y2)

        cost1 = math.ceil(d / p1)
        g[i].append((j, cost1))

        cost2 = math.ceil(d / p2)
        g[j].append((i, cost2))


lo, hi = 0, 4 * 10**9 + 1
while hi - lo > 1:
    # mi 以下の辺だけを利用して全ての頂点を回れるか？
    mi = (lo + hi) // 2

    for i in range(N):
        visited = [False] * N

        q = deque()
        q.append(i)
        visited[i] = True

        while q:
            u = q.pop()

            for v, cost in g[u]:
                if cost > mi:
                    continue
                if visited[v]:
                    continue
                visited[v] = True
                q.append(v)

        if all(visited):
            hi = mi
            break
    else:
        lo = mi

print(hi)
