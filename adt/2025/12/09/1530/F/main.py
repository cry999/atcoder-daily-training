H, W = map(int, input().split())

G = [input() for _ in range(H)]
visited = [[False]*W for _ in range(H)]

i, j = 0, 0
while True:
    if visited[i][j]:
        print(-1)
        break
    visited[i][j] = True
    if G[i][j] == 'U' and i > 0:
        i -= 1
        continue
    if G[i][j] == 'D' and i < H-1:
        i += 1
        continue
    if G[i][j] == 'L' and j > 0:
        j -= 1
        continue
    if G[i][j] == 'R' and j < W-1:
        j += 1
        continue
    print(i+1, j+1)
    break
