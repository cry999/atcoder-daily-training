while True:
    N, M = map(int, input().split())
    if N == M == 0:
        break
    C = [int(input()) for _ in range(M)]
    X = [int(input()) for _ in range(N)]

    INF = 10**18
    # dp[i] := y_n を i にするための最小コスト
    dp = [INF] * 256
    dp[128] = 0

    for x in X:
        ndp = [INF] * 256
        for y0 in range(256):
            for c in C:
                y = min(max(y0 + c, 0), 255)
                s = (x - y) ** 2
                ndp[y] = min(ndp[y], dp[y0] + s)
        dp = ndp

    print(min(dp))
