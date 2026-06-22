H, W = map(int, input().split())
S = [input() for _ in range(H)]

dist = [-1] * (H * W)

max_dist = 0
for h in range(H):
    for w in range(W):
        if S[h][w] == ".":
            sh, sw = h, w
            s = sh * W + sw
            for p in range(H * W):
                dist[p] = -1

            dist[s] = 0
            q = [s]

            for p in q:
                hh, ww = divmod(p, W)
                for dh, dw in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nh, nw = hh + dh, ww + dw
                    nn = nh * W + nw
                    if not (0 <= nh < H and 0 <= nw < W):
                        continue
                    if S[nh][nw] == "#":
                        continue
                    if 0 <= dist[nn] <= dist[p] + 1:
                        continue
                    dist[nn] = dist[p] + 1
                    max_dist = max(max_dist, dist[nn])
                    q.append(nn)

print(max_dist)
