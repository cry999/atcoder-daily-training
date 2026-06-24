MOD = 10**9 + 7

H, W, K = map(int, input().split())

bits = []
for bit in range(1 << (W - 1)):
    if bit & (bit << 1):
        continue
    bits.append(bit)
    print(f"[DEBUG] {bit=:0{W}b}")

dp = [[0] * W for _ in range(H + 1)]
dp[0][0] = 1

for h in range(H):
    # print(f"[DEBUG] {h=}")
    for bit in bits:
        # print(f"[DEBUG]   {bit=:0{W}b}")
        for j in range(W):
            nj = j
            if j > 0 and (bit >> (j - 1)) & 1:
                nj = j - 1
            elif j + 1 < W and (bit >> j) & 1:
                nj = j + 1
            dp[h + 1][nj] += dp[h][j]
            dp[h + 1][nj] %= MOD

print(dp[H][K - 1])
