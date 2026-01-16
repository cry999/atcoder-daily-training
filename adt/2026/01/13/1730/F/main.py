from collections import deque

N = int(input())

skill_tree = [[] for _ in range(N + 1)]

for i in range(N):
    a, b = map(int, input().split())
    skill_tree[a].append(i + 1)
    if a != b:
        skill_tree[b].append(i + 1)

queue = deque()
queue.append(0)
acquired = [False] * (N + 1)
acquired[0] = True

while queue:
    r = queue.popleft()
    for nxt in skill_tree[r]:
        if acquired[nxt]:
            continue
        acquired[nxt] = True
        queue.append(nxt)

print(sum(acquired[1:]))
