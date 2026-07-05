K = input()
L = len(K)
D = int(input())
MOD = 10**9 + 7

# dp[i][r][f] := 上位から i 桁目までを決めて、D で割ったあまりが r で K 以下かどうかが f で管理されている
dp = [[[0] * 2 for _ in range(D)] for _ in range(L + 1)]
dp[0][0][0] = 1

for i in range(L):  # 上位から i 桁目まで確定
    n = int(K[i])
    for r in range(D):  # D で割ったあまり
        for less in range(2):  # K 以下かどうかのフラグ
            # すでに上位が K より小さい場合はなんでも選べる。
            # まだ、K と同じ場合は K 以下に抑えるために n まで
            stop = 9 if less else n
            for d in range(stop + 1):
                nr = (r + d) % D
                nless = less or (d < n)
                dp[i + 1][nr][nless] += dp[i][r][less]
                dp[i + 1][nr][nless] %= MOD
print(sum(dp[L][0]) - 1)
