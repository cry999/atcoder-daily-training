from collections import deque

N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    u, v, w = map(int, input().split())
    u -= 1
    v -= 1

    g[u].append((v, w))
    g[v].append((u, w))

q = deque()
# ノード、通過状態, 重さ
q.append((0, 1, 0))

ans = 1 << 61
while q:
    u, state, weight = q.popleft()
    if u == N - 1:
        ans = min(ans, weight)

    for v, w in g[u]:
        mask = 1 << v
        if state & mask:
            # すでに通過している
            continue
        q.append((v, state | mask, weight ^ w))

print(ans)
