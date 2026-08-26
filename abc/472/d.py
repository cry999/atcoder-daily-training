H, W, K = map(int, input().split())
S = [input() for _ in range(H)]

INF = 10**18


is_safe = [False] * (H * W)
is_safe_row = [False] * H
is_safe_col = [False] * W

for h in range(H):
    is_safe_row[h] = all(S[h][w] == "." for w in range(W))

for w in range(W):
    is_safe_col[w] = all(S[h][w] == "." for h in range(H))

q = []
dist = [INF] * (H * W)
for p in range(H * W):
    h, w = divmod(p, W)
    is_safe[p] = is_safe_row[h] and is_safe_col[w]
    if is_safe[p]:
        q.append(p)
        dist[p] = 0

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
for p in q:
    h, w = divmod(p, W)
    for dh, dw in DIRS:
        nh, nw = h + dh, w + dw
        np = nh * W + nw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] == "#":
            continue
        if dist[np] <= dist[p] + 1:
            continue
        dist[np] = dist[p] + 1
        q.append(np)

# for p in range(H * W):
#     h, w = divmod(p, W)
#     if dist[p] == 0:
#         print(f"[DEBUG] {(h,w)=} {dist[p]=} {is_safe[p]=}")
ans = sum(dist[p] <= K for p in range(H * W))
print(ans)
