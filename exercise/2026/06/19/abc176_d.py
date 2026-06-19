from collections import deque

H, W = map(int, input().split())
ch, cw = map(lambda x: int(x) - 1, input().split())
gh, gw = map(lambda x: int(x) - 1, input().split())

S = [input() for _ in range(H)]

q = deque()
# pos, magic
q.append((ch * W + cw, 0))

INF = 10**9

magic = [-1] * (H * W)

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

while q:
    p, m = q.popleft()
    h, w = divmod(p, W)

    for dp in range(25):
        dh, dw = map(lambda x: x - 2, divmod(dp, 5))
        nh, nw = h + dh, w + dw

        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] == "#":
            continue

        dm = int(abs(dh) + abs(dw) > 1)

        np = nh * W + nw
        if 0 <= magic[np] <= m + dm:
            continue
        magic[np] = m + dm
        if dm == 0:
            q.appendleft((np, m + dm))
        else:
            q.append((np, m + dm))

print(magic[gh * W + gw])
