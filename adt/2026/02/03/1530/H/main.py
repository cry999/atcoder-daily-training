from collections import deque


N = int(input())

tree = [[] for _ in range(N)]

for _ in range(N - 1):
    u, v = map(lambda x: int(x) - 1, input().split())
    tree[u].append(v)
    tree[v].append(u)

queue = deque([(0, 0)])
color = [-1] * N
color[0] = 0

while queue:
    u, c = queue.popleft()

    for v in tree[u]:
        if color[v] != -1:
            continue
        color[v] = 1 - c
        queue.append((v, 1 - c))

# 相手の答えを覚えておく
used = [[False] * N for _ in range(N)]
# ついでに、すでに繋がれている辺も記憶しておく
for u in range(N):
    for v in tree[u]:
        used[u][v] = True

# 答えに使える辺
edges = []
for u in range(N):
    for v in range(u + 1, N):
        if color[u] != color[v] and not used[u][v]:
            edges.append((u, v))


my_turn = True
if len(edges) % 2 == 0:
    print("Second")
    my_turn = False
else:
    print("First")

i = 0
while True:
    if my_turn:
        while True:
            u, v = edges[i]
            i += 1
            if used[u][v]:
                continue
            print(u + 1, v + 1)
            used[u][v] = used[v][u] = True
            break
    else:
        u, v = map(lambda x: int(x) - 1, input().split())
        if u == v == -2:
            break
        used[u][v] = used[v][u] = True

    my_turn = not my_turn
