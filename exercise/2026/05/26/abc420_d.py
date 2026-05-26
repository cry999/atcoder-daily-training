from collections import deque

H, W = map(int, input().split())
A = [input() for _ in range(H)]

sh, sw = -1, -1
gh, gw = -1, -1

for h in range(H):
    for w in range(W):
        if A[h][w] == "S":
            sh, sw = h, w
        elif A[h][w] == "G":
            gh, gw = h, w

dist = [[[float("inf")] * 2 for _ in range(W)] for _ in range(H)]
dist[sh][sw][0] = 0

# (h, w, cost, switch)
q = deque([(sh, sw, 0, False)])

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

while q:
    h, w, cost, switch = q.popleft()
    if h == gh and w == gw:
        print(cost)
        break

    for dh, dw in DIRS:
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if A[nh][nw] == "#":
            continue
        if switch and A[nh][nw] == "o":
            continue
        if not switch and A[nh][nw] == "x":
            continue
        nxt_switch = switch
        if A[nh][nw] == "?":
            nxt_switch = not switch

        if dist[nh][nw][nxt_switch] <= cost + 1:
            continue
        dist[nh][nw][nxt_switch] = cost + 1
        q.append((nh, nw, cost + 1, nxt_switch))
else:
    print(-1)
