N = int(input())
A = [int(input()) for _ in range(N)]

# 一周するので A を2倍にして処理しやすくする。
for i in range(N):
    A.append(A[i])
# dp[i][d] := i から i+d までのケーキのピースが残っている時の最大スコア
dp = [[0] * (N + 1) for _ in range(2 * N)]

for d in range(1, N + 1):
    if d % 2 != N % 2:
        continue
    for i in range(N):
        # (i, i+d-1) の範囲の d ピースのケーキが残っている。
        # JOI 君の選択肢は i と i+d のどちらか。
        # その後、IOI ちゃんは残っている方の大きい方をとる。
        # (残っていれば)
        if d == 1:
            # JOI 君がとって終わり。
            dp[i][d] = A[i]
        else:
            # JOI 君が i をとる場合
            if A[i + 1] > A[i + d - 1]:
                # IOI ちゃんは i+1 をとる。
                dp[i][d] = max(dp[i][d], A[i] + dp[(i + 2) % N][d - 2])
            else:
                # IOI ちゃんは i+d をとる。
                dp[i][d] = max(dp[i][d], A[i] + dp[(i + 1) % N][d - 2])

            # JOI 君が i+d をとる場合
            if A[i] > A[i + d - 2]:
                # IOI ちゃんは i をとる。
                dp[i][d] = max(dp[i][d], A[i + d - 1] + dp[(i + 1) % N][d - 2])
            else:
                # IOI ちゃんは i+d-1 をとる。
                dp[i][d] = max(dp[i][d], A[i + d - 1] + dp[i][d - 2])
ans = 0
for i in range(N):
    # どの i から取り始めるのが最適か
    ans = max(ans, dp[i][N])
print(ans)
