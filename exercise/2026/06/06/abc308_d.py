from collections import deque

H, W = map(int, input().split())
S = [input() for _ in range(H)]

if S[0][0] != "s":
    print("No")
    exit()

SNUKE = "snuke"
REV = {c: i for i, c in enumerate(SNUKE)}

q = deque()
dist = [-1] * (H * W)
q.append(0)

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

while q:
    pos = q.popleft()
    i, j = divmod(pos, W)

    cur = REV[S[i][j]]

    for di, dj in DIRS:
        ni, nj = i + di, j + dj
        if not (0 <= ni < H and 0 <= nj < W):
            continue
        if S[ni][nj] != SNUKE[(cur + 1) % len(SNUKE)]:
            continue
        npos = ni * W + nj
        if 0 <= dist[npos] <= dist[pos] + 1:
            continue
        dist[npos] = dist[pos] + 1
        q.append(npos)

if dist[-1] == -1:
    print("No")
else:
    print("Yes")
