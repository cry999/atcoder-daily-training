MOD = 998244353

S = input()
N = len(S)

# dp[i][c] := i 文字目までの利用有無を決めて、末端の文字が ''(0), a(1), b(2), c(3) になる
# 部分文字列の場合の数
dp = [[0] * 4 for _ in range(N + 1)]
dp[0][0] = 1

for i in range(N):
    for c in range(4):
        dp[i + 1][c] = dp[i][c]  # i 文字目を利用しない場合

    # i 文字目を利用する場合
    if S[i] == "a":
        dp[i + 1][1] += sum(dp[i][c] for c in range(4) if c != 1)
    elif S[i] == "b":
        dp[i + 1][2] += sum(dp[i][c] for c in range(4) if c != 2)
    elif S[i] == "c":
        dp[i + 1][3] += sum(dp[i][c] for c in range(4) if c != 3)

    for c in range(4):
        dp[i + 1][c] %= MOD

print(sum(dp[N][c] for c in range(1, 4)) % MOD)
