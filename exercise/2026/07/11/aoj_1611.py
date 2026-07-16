while True:
    N = int(input())
    if N == 0:
        break
    (*w,) = map(int, input().split())

    dp = [[0] * N for _ in range(N)]
    # 初期化
    for i in range(N - 1):
        # 隣り合うブロックの重さの差が 1 以下なら落とせる
        if abs(w[i] - w[i + 1]) <= 1:
            dp[i][i + 1] = 2
    for i in range(N):
        # 1 つだけ落とすことはできないので 0
        dp[i][i] = 0

    for d in range(2, N):
        for l in range(N):
            r = l + d
            if r >= N:
                break

            # (l, r) で考えることは、
            # 1. (l, k), (k+1, r) の最大値の和、の最大値
            # 2. (l+1, r-1) が全部落とせて w[l] と w[r] の重さの差が 1 以下
            if dp[l + 1][r - 1] == r - l - 1 and abs(w[l] - w[r]) <= 1:
                # 条件 2: この場合は全部落とせるので絶対に最大
                dp[l][r] = r - l + 1
            else:
                # 条件 1:
                for k in range(l, r):
                    dp[l][r] = max(dp[l][r], dp[l][k] + dp[k + 1][r])
    print(dp[0][N - 1])
