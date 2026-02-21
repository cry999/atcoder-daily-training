from collections import deque

N, K = map(int, input().split())
C = [list(map(int, input().split())) for _ in range(N)]


def hash_list(a: list[int]) -> int:
    h = 0
    for x in a:
        # 0 <= x < 7 の想定
        h = (h << 3) | x
    return h


def score(a: list[int]) -> int:
    s = 0
    for i in range(N):
        s += C[a[i]][a[(i + 1) % N]]
    return s


# (企業の列, 操作回数)
queue = deque()
queue.append(([i for i in range(N)], 0))

visited = set()


ans = 0
while queue:
    a, k = queue.popleft()
    ans = max(ans, score(a))
    if k == K:
        continue

    for i in range(N):
        for j in range(N):
            b = a[:]
            b[i], b[j] = b[j], b[i]

            h = hash_list(b)
            if h in visited:
                continue
            visited.add(h)
            queue.append((b, k + 1))

print(ans)
