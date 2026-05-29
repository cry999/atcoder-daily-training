import sys
from collections import deque

input = sys.stdin.readline
print = sys.stdout.write

H, W = map(int, input().split())
S = [list(input()) for _ in range(H)]

q = deque()
for h in range(H):
    for w in range(W):
        if S[h][w] == "E":
            q.append((h, w))

DIRS = [(-1, 0, "v"), (1, 0, "^"), (0, -1, ">"), (0, 1, "<")]

while q:
    h, w = q.popleft()

    for dh, dw, c in DIRS:
        nh, nw = h + dh, w + dw
        if (0 <= nh < H and 0 <= nw < W) and S[nh][nw] == ".":
            S[nh][nw] = c
            q.append((nh, nw))


print("".join("".join(r) for r in S))
