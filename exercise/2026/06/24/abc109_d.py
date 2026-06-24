H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]

op = []
for h in range(H):
    for w in range(W):
        if A[h][w] % 2 == 0:
            continue
