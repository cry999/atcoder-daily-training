from collections import deque

N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

g = [[] for _ in range(N)]
for i in range(M):
    a, b = A[i] - 1, B[i] - 1
    g[a].append(b)
    g[b].append(a)

color = [-1] * N


def bfs(u: int):
    color[i] = 0
    q = deque()
    q.append((i, color[i]))

    while q:
        u, c = q.popleft()

        for v in g[u]:
            if color[v] == 1 - c:
                # ok
                continue
            if color[v] != -1:
                # ng
                return False
            color[v] = 1 - c
            q.append((v, 1 - c))

    return True


for i in range(N):
    if color[i] != -1:
        continue

    if not bfs(i):
        print("No")
        break
else:
    print("Yes")
