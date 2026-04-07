from collections import deque

N = int(input())

skill_tree = [[] for _ in range(N)]
q = deque()
acquired = [False] * N

for i in range(N):
    a, b = map(int, input().split())
    if a == 0 and b == 0:
        q.append(i)
        acquired[i] = True
    else:
        skill_tree[a - 1].append(i)
        skill_tree[b - 1].append(i)

while q:
    skill = q.popleft()

    for next_skill in skill_tree[skill]:
        if acquired[next_skill]:
            continue
        acquired[next_skill] = True
        q.append(next_skill)

print(sum(acquired))
