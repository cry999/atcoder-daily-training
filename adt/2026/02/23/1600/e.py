from collections import deque

N, X, Y = map(int, input().split())
tree = [[] for _ in range(N + 1)]

for _ in range(N - 1):
    u, v = map(int, input().split())
    tree[u].append(v)
    tree[v].append(u)

from_node = [-1] * (N + 1)

q = deque([Y])
from_node[Y] = 0

while q:
    u = q.popleft()

    for v in tree[u]:
        if from_node[v] != -1:
            # visited
            continue
        from_node[v] = u

        if v == X:
            q = None
            break

        q.append(v)

ans = []
cur = X
while cur != 0:
    ans.append(cur)
    cur = from_node[cur]

print(*ans)
