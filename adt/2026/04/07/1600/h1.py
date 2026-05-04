N = int(input())
S = input()

MOD = 998244353

# dp[i][S][c]:
# - i 文字目までの利用可否を決めていて、
# - 文字の使用状況が S であり、
# - 最後の文字列が c であるような場合の数
dp = [[[0] * 10 for _ in range(1 << 10)] for _ in range(N + 1)]
dp[0][0][0] = 1

for i in range(N):
    c = ord(S[i]) - ord("A")
    for s in range(1 << 10):
        # S[i] を使わない場合:
        for cc in range(10):
            dp[i + 1][s][cc] += dp[i][s][cc]

        # S[i] を使う場合:
        if s & (1 << c):
            # すでに c を使っている場合は、最後に使った文字が c でないといけない
            dp[i + 1][s][c] += dp[i][s][c]
            dp[i + 1][s][c] %= MOD
        else:
            # まだ c を使っていない場合は、最後の文字は問わない。
            dp[i + 1][s | (1 << c)][c] += sum(dp[i][s])
            dp[i + 1][s | (1 << c)][c] %= MOD

ans = 0
for s in range(1, 1 << 10):
    ans += sum(dp[N][s])
    ans %= MOD

print(ans)
