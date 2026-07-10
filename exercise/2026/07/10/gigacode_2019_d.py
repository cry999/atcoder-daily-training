H, W, K, V = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]

C = [[0] * (W + 1) for _ in range(H + 1)]
for h in range(H):
    for w in range(W):
        C[h + 1][w + 1] += C[h + 1][w] + A[h][w]
for h in range(H):
    for w in range(W + 1):
        C[h + 1][w] += C[h][w]


def price(h1: int, h2: int, w1: int, w2: int):
    """引数は 0-indexed で h1 <= h2, w1 <= w2 の想定"""
    return (
        C[h2 + 1][w2 + 1]
        - C[h2 + 1][w1]
        - C[h1][w2 + 1]
        + C[h1][w1]
        + (h2 - h1 + 1) * (w2 - w1 + 1) * K
    )


ans = 0
for h1 in range(H):
    for h2 in range(h1, H):
        w2 = 0
        for w1 in range(W):
            w2 = max(w2, w1)
            while w2 < W and price(h1, h2, w1, w2) <= V:
                ans = max(ans, (h2 - h1 + 1) * (w2 - w1 + 1))
                w2 += 1
print(ans)
