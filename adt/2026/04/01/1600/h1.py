H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]
(*P,) = map(int, input().split())

# B[h][w]: -((h, w) からスタートすると仮定した場合に事前に必要になるコインの枚数)
B = [[A[h][w] - P[h + w] for w in range(W)] for h in range(H)]


for h in range(H - 1, -1, -1):
    for w in range(W - 1, -1, -1):
        if h + 1 < H and w + 1 < W:
            B[h][w] += max(B[h + 1][w], B[h][w + 1])
        elif h + 1 < H:
            B[h][w] += B[h + 1][w]
        elif w + 1 < W:
            B[h][w] += B[h][w + 1]

        B[h][w] = min(B[h][w], 0)

print(-B[0][0])
