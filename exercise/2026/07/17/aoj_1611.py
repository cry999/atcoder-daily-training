def solve(n: int, w: list[int]):
    # dp[l][r] := 上から l 番目から r 番目までの最大叩き落とし数
    dp = [[0] * n for _ in range(n)]
    for i in range(N - 1):
        dp[i][i + 1] = 2 if abs(w[i] - w[i + 1]) <= 1 else 0

    for d in range(2, N):
        for l in range(N - d):
            r = l + d

            if dp[l + 1][r - 1] == r - l - 1 and abs(w[l] - w[r]) <= 1:
                dp[l][r] = r - l + 1
            else:
                for k in range(l, r):
                    dp[l][r] = max(dp[l][r], dp[l][k] + dp[k + 1][r])

    return dp[0][N - 1]


while True:
    N = int(input())
    if not N:
        break
    (*W,) = map(int, input().split())

    ans = solve(N, W)
    print(ans)
