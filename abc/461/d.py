H, W, K = map(int, input().split())
S = [input() for _ in range(H)]

C = [[0] * (W + 1) for _ in range(H + 1)]
for i in range(H):
    for j in range(W):
        C[i + 1][j + 1] = C[i][j + 1] + int(S[i][j])

for i in range(H + 1):
    for j in range(W):
        C[i][j + 1] += C[i][j]


def area(h1: int, h2: int, w1: int, w2: int):
    return C[h2][w2] - C[h2][w1] - C[h1][w2] + C[h1][w1]


# print(C)

ans = 0
for h1 in range(H):
    for h2 in range(h1 + 1, H + 1):
        w2, w3 = 1, 1
        for w1 in range(W):
            w2 = max(w2, w1 + 1)
            while w2 <= W and area(h1, h2, w1, w2) < K:
                # print(" ", area(h1, h2, w1, w2))
                w2 += 1

            w3 = max(w3, w2)
            while w3 <= W and area(h1, h2, w1, w3) == K:
                # print(" ", area(h1, h2, w1, w3))
                w3 += 1

            ans += w3 - w2


print(ans)
