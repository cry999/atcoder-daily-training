from math import factorial
from itertools import permutations
from collections import deque

M = int(input())
g = [[] for _ in range(9)]

for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append(v)
    g[v].append(u)

(*p,) = map(int, input().split())

indexes = {perm: i for i, perm in enumerate(permutations(range(9)))}


# state[i] := マス i にある駒の数字にしたい。0 が空きマス。
q = [0] * 9
for piece, pos in enumerate(p):
    q[pos - 1] = piece + 1

state = tuple(q)
goal_state = tuple((i + 1) % 9 for i in range(9))

queue = deque()
queue.append(state)

dist = [-1] * factorial(9)
dist[indexes[state]] = 0

while queue:
    s = queue.popleft()
    si = indexes[s]
    if s == goal_state:
        break

    # 1. 空きマスを見つける
    # 2. 空きマスとつながっているマスから駒の移動を試みる
    # 3. 次の状態とする
    empty = 0
    for u, piece in enumerate(s):
        if piece == 0:
            empty = u
            break

    for v in g[empty]:
        t = tuple(0 if i == v else (s[v] if i == empty else s[i]) for i in range(9))
        ti = indexes[t]
        if dist[ti] >= 0:
            continue
        dist[ti] = dist[si] + 1
        if t == goal_state:
            break
        queue.append(t)
    else:
        continue
    break

print(dist[indexes[goal_state]])
