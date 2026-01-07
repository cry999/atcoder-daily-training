MOD = 10**9 + 7
N = int(input())
a = [tuple(map(int, input().split())) for _ in range(N)]

# dp[i][S] := i 番目までの男性を S に含まれる女性とペアにする場合の数
dp = [[0] * (1 << N) for _ in range(N + 1)]
dp[0][0] = 1

for i in range(N):
    for s in range(1 << N):
        if dp[i][s] == 0:
            continue
        for j in range(N):
            if s & (1 << j):
                continue
            if a[i][j] == 0:
                continue
            dp[i + 1][s | (1 << j)] += dp[i][s]
            dp[i + 1][s | (1 << j)] %= MOD

print(dp[-1][-1])
