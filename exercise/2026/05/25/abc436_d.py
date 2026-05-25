from collections import deque
import sys

input = sys.stdin.readline

H, W = map(int, input().split())
S = [input() for _ in range(H)]

sh, sw = 0, 0
q = deque([0])

warps = [[] for _ in range(26)]
ord_a = ord("a")
for h in range(H):
    for w in range(W):
        if S[h][w] in ".#":
            continue
        warps[ord(S[h][w]) - ord_a].append(h * W + w)

dist = [-1] * (H * W)
dist[0] = 0

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

while q:
    n = q.popleft()
    cost = dist[n]
    h, w = n // W, n % W

    for dh, dw in DIRS:
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] == "#":
            continue
        p = nh * W + nw
        if 0 <= dist[p] <= cost + 1:
            continue
        dist[p] = cost + 1
        if nh == H - 1 and nw == W - 1:
            print(cost + 1)
            exit()
        q.append(p)

    if not (0 <= ord(S[h][w]) - ord_a < 26):
        continue

    while warps[ord(S[h][w]) - ord_a]:
        n = warps[ord(S[h][w]) - ord_a].pop()
        nh, nw = n // W, n % W
        if nh == h and nw == w:
            continue
        p = nh * W + nw
        if 0 <= dist[p] <= cost + 1:
            continue
        dist[p] = cost + 1
        if nh == H - 1 and nw == W - 1:
            print(cost + 1)
            exit()
        q.append(p)

print(dist[-1])
