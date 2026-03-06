from collections import deque

N, M = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    u, v = map(int, input().split())
    g[u].append(v)
    g[v].append(u)

K = int(input())

visited = [False] * (N + 1)


def clear_visited():
    for i in range(N + 1):
        visited[i] = False
    return


candidates = [[] for _ in range(N + 1)]
is_black = [True] * (N + 1)
is_black[0] = False

for _ in range(K):
    p, d = map(int, input().split())

    clear_visited()

    q = deque()
    q.append((p, d))
    while q:
        u, r = q.popleft()
        if r == 0:
            candidates[p].append(u)
            continue
        is_black[u] = False

        for v in g[u]:
            if visited[v]:
                continue
            visited[v] = True
            q.append((v, r - 1))

if not any(is_black):
    print("No")
    exit()

for i in range(1, N + 1):
    if not candidates[i]:
        continue

    if any(is_black[v] for v in candidates[i]):
        # 少なくとも 1 つが黒であれば OK
        continue

    print("No")
    break
else:
    print("Yes")
    print("".join(map(lambda x: "1" if x else "0", is_black[1:])))
