A, B, C = map(int, input().split())

# dp[a][b][c] = 金貨 A 枚、銀貨 B 枚, 銅貨 C 枚から、いずれかが 100 枚になる期待値
dp = [[[0.0] * 101 for _ in range(101)] for _ in range(101)]


for a in range(99, -1, -1):
    for b in range(99, -1, -1):
        for c in range(99, -1, -1):
            if a == b == c == 0:
                continue

            dp[a][b][c] += (dp[a + 1][b][c] + 1) * a / (a + b + c)
            dp[a][b][c] += (dp[a][b + 1][c] + 1) * b / (a + b + c)
            dp[a][b][c] += (dp[a][b][c + 1] + 1) * c / (a + b + c)

print(dp[A][B][C])
