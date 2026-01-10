from collections import deque


H, W = map(int, input().split())
S = [input() for _ in range(H)]
visited = [[0] * W for _ in range(H)]

ans = 0
for i in range(H):
    for j in range(W):
        if S[i][j] == ".":
            continue
        if visited[i][j]:
            continue

        ans += 1

        queue = deque()
        queue.append((i, j))
        while queue:
            ci, cj = queue.popleft()
            if visited[ci][cj]:
                continue
            visited[ci][cj] = ans

            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    ni, nj = ci + di, cj + dj
                    if not (0 <= ni < H and 0 <= nj < W):
                        continue
                    if S[ni][nj] == ".":
                        continue
                    if visited[ni][nj]:
                        continue
                    queue.append((ni, nj))
print(ans)
