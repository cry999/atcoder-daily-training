from collections import deque

H, W = map(int, input().split())
S = [input() for _ in range(H)]

start = 1 * W + 1

q = deque()
q.append(start)

visited = [False] * (H * W)
visited[start] = True

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

while q:
    pos = q.popleft()
    i, j = divmod(pos, W)

    for di, dj in DIRS:
        ni, nj = i + di, j + dj
        if not (0 <= ni < H and 0 <= nj < W):
            continue
        if S[ni][nj] == "#":
            continue

        ti, tj = ni, nj
        all_visited = visited[ti * W + tj]
        while S[ti + di][tj + dj] == "." and all_visited:
            ti += di
            tj += dj
            all_visited = all_visited and visited[ti * W + tj]

        if all_visited:
            continue

        visited[ni * W + nj] = True
        while S[ni + di][nj + dj] == ".":
            ni += di
            nj += dj
            visited[ni * W + nj] = True

        q.append(ni * W + nj)


print(sum(visited))
