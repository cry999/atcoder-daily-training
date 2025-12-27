import heapq


H, W = map(int, input().split())
A = [input() for _ in range(H)]

# (移動距離, (h, w), スイッチの状態)
queue = []
for h in range(H):
    for w in range(W):
        if A[h][w] == 'S':
            S = (h, w)
        if A[h][w] == 'G':
            G = (h, w)

heapq.heappush(queue, (0, S, 0))

dists = [[[float('inf')]*2 for _ in range(W)] for _ in range(H)]

while queue:
    dist, (h, w), sw = heapq.heappop(queue)
    if (h, w) == G:
        print(dist)
        exit()

    if dists[h][w][sw] <= dist:
        continue
    dists[h][w][sw] = dist

    if A[h][w] == '?':
        sw = 1-sw

    walls = set(['#', 'o' if sw else 'x'])
    for dh, dw in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nh, nw = h+dh, w+dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if A[nh][nw] in walls:
            continue
        if dists[nh][nw][sw] <= dist+1:
            continue
        heapq.heappush(queue, (dist+1, (nh, nw), sw))


print(-1)
