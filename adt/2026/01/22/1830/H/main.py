K = int(input())
(*C,) = map(int, input().split())

MOD = 998244353

comb = [[0] * (K + 1) for _ in range(K + 1)]
comb[0][0] = 1

for i in range(K):
    comb[i + 1][0] = comb[i][0]
    for j in range(K):
        comb[i + 1][j + 1] = (comb[i][j] + comb[i][j + 1]) % MOD

# dp[i][k] := 文字 a_1, .., a_i を使って長さ K の文字を作る方法の数
dp = [[0] * (K + 1) for _ in range(26 + 1)]
dp[0][0] = 1
for i in range(26):
    for j in range(K + 1):
        for k in range(min(C[i], j) + 1):
            dp[i + 1][j] += dp[i][j - k] * comb[j][k]
            dp[i + 1][j] %= MOD

print(sum(dp[26][1:]) % MOD)
