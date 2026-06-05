from collections import deque

H, W = map(int, input().split())
A = [input() for _ in range(H)]

E = [[0] * W for _ in range(H)]
N = int(input())
for _ in range(N):
    r, c, e = map(int, input().split())
    E[r - 1][c - 1] = e

visited = [[-1] * W for _ in range(H)]
q = deque()
for r in range(H):
    for c in range(W):
        if A[r][c] == "S":
            q.append((r, c, 0))
            visited[r][c] = 0
            break

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
while q:
    r, c, e = q.popleft()
    e = max(E[r][c], e)
    # print(f"{r=}, {c=}, {e=}")
    if e == 0:
        continue

    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if not (0 <= nr < H and 0 <= nc < W):
            continue
        if A[nr][nc] == "#":
            continue
        if visited[nr][nc] >= e - 1:
            continue
        visited[nr][nc] = e - 1
        if A[nr][nc] == "T":
            print("Yes")
            break
        q.append((nr, nc, e - 1))
    else:
        continue
    break
else:
    print("No")
