H, W = map(int, input().split())
S = [list(input()) for _ in range(H)]

for h in range(H):
    for w in range(W - 1):
        if "".join(S[h][w : w + 2]) == "TT":
            S[h][w] = "P"
            S[h][w + 1] = "C"

print("\n".join("".join(row) for row in S))
