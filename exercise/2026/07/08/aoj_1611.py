while True:
    N = int(input())
    if not N:
        break

    (*W,) = map(int, input().split())

    # dp[l][r] := [l, r] を叩き落とせるか?
    dp = [[0] * N for _ in range(N)]
    for d in range(1, N):
        for l in range(N):
            r = l + d
            if r >= N:
                break

            if d == 1:
                if -1 <= W[r] - W[l] <= 1:
                    dp[l][r] = d + 1
            else:
                if dp[l + 1][r - 1] == d - 1 and -1 <= W[r] - W[l] <= 1:
                    dp[l][r] = d + 1
                for k in range(l + 1, r + 1):
                    dp[l][r] = max(dp[l][r], dp[l][k - 1] + dp[k][r])

    print(dp[0][N - 1])
