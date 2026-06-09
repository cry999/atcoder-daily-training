from collections import deque

N = int(input())
sx, sy, tx, ty = map(int, input().split())

# 1. (sx, sy), (tx, ty) がどの円の上にあるか (cs, ct)
# 2. 円をノード, 円が交わり関係を辺にグラフを作る
# 3. cs から ct に到達できるか

circles = [tuple(map(int, input().split())) for _ in range(N)]


def intersect(i: int, j: int):
    x1, y1, r1 = circles[i]
    x2, y2, r2 = circles[j]
    d = (x1 - x2) ** 2 + (y1 - y2) ** 2
    return (r1 - r2) ** 2 <= d <= (r1 + r2) ** 2


def is_on(i: int, x: int, y: int):
    rx, ry, r = circles[i]
    return (rx - x) ** 2 + (ry - y) ** 2 == r**2


g = [[] for _ in range(N)]
cs, ct = -1, -1
for i in range(N):
    if cs == -1 and is_on(i, sx, sy):
        cs = i
    if ct == -1 and is_on(i, tx, ty):
        ct = i

    for j in range(i + 1, N):
        if intersect(i, j):
            g[i].append(j)
            g[j].append(i)

assert cs != -1 and ct != -1

visited = [False] * N
q = deque()
q.append(cs)
visited[cs] = True

while q:
    u = q.popleft()
    for v in g[u]:
        if visited[v]:
            continue
        visited[v] = True
        if v == ct:
            break
        q.append(v)
    else:
        continue
    break

print("Yes" if visited[ct] else "No")
