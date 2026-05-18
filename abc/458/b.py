H, W = map(int, input().split())
ans = [[0] * W for _ in range(H)]

for h in range(H):
    for w in range(W):
        ans[h][w] += h + 1 < H
        ans[h][w] += h - 1 >= 0
        ans[h][w] += w + 1 < W
        ans[h][w] += w - 1 >= 0

for row in ans:
    print(*row)
