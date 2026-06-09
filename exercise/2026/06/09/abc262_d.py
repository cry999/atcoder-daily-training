MOD = 998244353

N = int(input())
(*A,) = map(int, input().split())

ans = 0
for m in range(1, N + 1):
    # m: 選ぶ個数
    # dp[i][k][d] :=
    #   i 個目までを選ぶか決めて
    #   k 個 (最大 m 個) 選んだ時の総和を
    #   m で割ったあまりが d になる選び方
    dp = [[[0] * m for _ in range(m + 1)] for _ in range(N + 1)]
    dp[0][0][0] = 1

    for i in range(N):
        for k in range(m + 1):
            for d in range(m):
                # 選ばない
                dp[i + 1][k][d] += dp[i][k][d]
                dp[i + 1][k][d] %= MOD
                # 選ぶ
                if k + 1 <= m:
                    dp[i + 1][k + 1][(d + A[i]) % m] += dp[i][k][d]
                    dp[i + 1][k + 1][(d + A[i]) % m] %= MOD

    # print(f"[DEBUG] {m=}, {dp=}")
    ans += dp[N][m][0]
    ans %= MOD
print(ans)
