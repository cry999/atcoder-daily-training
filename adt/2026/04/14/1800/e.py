H, W = map(int, input().split())
S = [input() for _ in range(H)]

for h in range(H):
    for w in range(W):
        if S[h][w] == "#":
            continue
        # 周囲 4 ますのうち、# が 2 つ以上あれば良い。
        cnt = 0
        for dh, dw in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nh, nw = h + dh, w + dw
            if 0 <= nh < H and 0 <= nw < W and S[nh][nw] == "#":
                cnt += 1
        if cnt >= 2:
            print(h + 1, w + 1)
            exit()
