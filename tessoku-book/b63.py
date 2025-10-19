import heapq


R, C = map(int, input().split())
sy, sx = map(int, input().split())
gy, gx = map(int, input().split())
c = [input() for _ in range(R)]
d = [[-1]*C for _ in range(R)]

queue = [(0, sy-1, sx-1)]
while queue:
    dist, y, x = heapq.heappop(queue)
    for dy, dx in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        ny, nx = y+dy, x+dx
        if ny < 0 or R <= ny or nx < 0 or C <= nx:
            continue
        if d[ny][nx] != -1:
            continue
        if c[ny][nx] == '#':
            continue
        if ny == gy-1 and nx == gx-1:
            print(dist+1)
            exit()
        d[ny][nx] = dist+1
        heapq.heappush(queue, (dist+1, ny, nx))
