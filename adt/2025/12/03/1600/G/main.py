import heapq


H, W = map(int, input().split())
C = [input() for _ in range(H)]

queue = [(-1, 0, 0)]
routes = [[0] * W for _ in range(H)]

ans = 0
while queue:
    depth, i, j = heapq.heappop(queue)
    depth = -depth

    if routes[i][j] >= depth:
        continue
    routes[i][j] = depth
    ans = max(ans, depth)
    if i+1 < H and C[i+1][j] == '.':
        heapq.heappush(queue, (-depth-1, i+1, j))
    if j+1 < W and C[i][j+1] == '.':
        heapq.heappush(queue, (-depth-1, i, j+1))

print(ans)
