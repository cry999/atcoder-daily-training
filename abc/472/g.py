from atcoder.maxflow import MFGraph

H, W = map(int, input().split())
S = [input() for _ in range(H)]

N = H * W
s, t = N, N + 1
g = MFGraph(N + 2)

ans = 0
INF = 10**18

for p in range(H * W):
    h, w = divmod(p, W)

    if S[h][w] == "#":
        continue
    if S[h][w] == "+":
        g.add_edge(s, p, 1)
        ans += 1
    else:
        g.add_edge(p, t, 1)

    if w + 1 < W and S[h][w + 1] != "#":
        g.add_edge(p, p + 1, INF)
        g.add_edge(p + 1, p, INF)
    if h + 1 < H and S[h + 1][w] != "#":
        g.add_edge(p + W, p, INF)

ans -= g.flow(s, t)
print(ans)
