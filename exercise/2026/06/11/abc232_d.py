from collections import deque

H, W = map(int, input().split())
S = [input() for _ in range(H)]

q = deque()
q.append(0)

dist = [-1] * (H * W)
dist[0] = 1

ans = 1
while q:
    pos = q.popleft()
    i, j = divmod(pos, W)

    ni, nj = i + 1, j
    npos = ni * W + nj
    if ni < H and S[ni][nj] != "#" and dist[npos] == -1:
        dist[npos] = dist[pos] + 1
        ans = max(dist[npos], ans)
        q.append(npos)

    ni, nj = i, j + 1
    npos = ni * W + nj
    if nj < W and S[ni][nj] != "#" and dist[npos] == -1:
        dist[npos] = dist[pos] + 1
        ans = max(dist[npos], ans)
        q.append(npos)

print(ans)
