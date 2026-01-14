from collections import deque

H, W = map(int, input().split())
S = [list(input()) for _ in range(H)]

sh, sw = -1, -1
gh, gw = -1, -1
for h in range(H):
    for w in range(W):
        if S[h][w] == "S":
            sh, sw = h, w
        elif S[h][w] == "G":
            gh, gw = h, w
        elif S[h][w] == ">":
            for nw in range(w + 1, W):
                if S[h][nw] not in ".!":
                    break
                S[h][nw] = "!"
        elif S[h][w] == "<":
            for nw in range(w - 1, -1, -1):
                if S[h][nw] not in ".!":
                    break
                S[h][nw] = "!"
        elif S[h][w] == "^":
            for nh in range(h - 1, -1, -1):
                if S[nh][w] not in ".!":
                    break
                S[nh][w] = "!"
        elif S[h][w] == "v":
            for nh in range(h + 1, H):
                if S[nh][w] not in ".!":
                    break
                S[nh][w] = "!"


visited = [[float("inf")] * W for _ in range(H)]
queue = deque()
queue.append((0, sh, sw))
visited[sh][sw] = 0


while queue:
    neg_dist, h, w = queue.popleft()
    dist = -neg_dist
    if (h, w) == (gh, gw):
        break

    for dh, dw in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] not in ".SG":
            continue
        if visited[nh][nw] <= dist + 1:
            continue
        visited[nh][nw] = dist + 1
        queue.append((-(dist + 1), nh, nw))

if visited[gh][gw] == float("inf"):
    print(-1)
else:
    print(visited[gh][gw])
