N, M = map(int, input().split())
plushes = [int(input()) - 1 for _ in range(N)]
# cum[m][i] := i 番目までに並んでいる種類 m のぬいぐるみの個数
cum = [[0] * (N + 1) for _ in range(M)]
for i in range(N):
    for m in range(M):
        cum[m][i + 1] = cum[m][i] + (plushes[i] == m)

INF = 10**18
dp = [INF] * (1 << M)
dp[0] = 0
for s in range(1 << M):
    for m in range(M):
        if s & (1 << m):
            # すでに並べてあるなら対象外
            continue

        ns = s | (1 << m)
        # すでに左に並べてあるぬいぐるみの総数
        left = sum(cum[i][N] for i in range(M) if s & (1 << i))
        # ぬいぐるみ m を並べる最右端
        right = left + cum[m][N]
        # ぬいぐるみ m は [left, right) に並べる。(0-indexed)
        # n0: この区間に元々あるぬいぐるみ
        n0 = cum[m][right] - cum[m][left]
        # n1: 移動するぬいぐるみ
        n1 = right - left - n0
        dp[ns] = min(dp[ns], dp[s] + n1)

ALL = (1 << M) - 1
print(dp[ALL])
