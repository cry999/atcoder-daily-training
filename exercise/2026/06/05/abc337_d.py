H, W, K = map(int, input().split())
S = [input() for _ in range(H)]

ans = float("inf")
for h in range(H):
    k = 0
    num_o = 0
    for w in range(W):
        if S[h][w] == "x":
            k = 0
            num_o = 0
        else:
            k += 1
            num_o += S[h][w] == "o"

        if k == K:
            ans = min(ans, K - num_o)
            num_o -= S[h][w - K + 1] == "o"
            k -= 1

for w in range(W):
    k = 0
    num_o = 0
    for h in range(H):
        if S[h][w] == "x":
            k = 0
            num_o = 0
        else:
            k += 1
            num_o += S[h][w] == "o"

        if k == K:
            ans = min(ans, K - num_o)
            num_o -= S[h - K + 1][w] == "o"
            k -= 1

print(ans if ans != float("inf") else -1)
