# >>> atcoder-stat >>>
# started_at  = 2026-10-10T10:56:01+09:00
# solved_at   = 2026-10-10T11:29:05+09:00
# duration_ms = 1984738
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, Q, X = map(int, input().split())
(*W,) = map(int, input().split())

# 考察
# W のどの位置から始まる和を考えるのか
# この「どの位置から始まる」については、循環しているし、有向グラフになるはず
# 問題は 2 つ。
# 1. X 以上になるまでの和を作るには？ X が大きいので、工夫しないといけない。
#   -> これは、累積和を使うと良い。累積和の全体で divmod(X) すると良さそう。
# 2. グラフの作り方。
#   -> これは、まず、各 i からどの i まで利用するかを求める。

# 循環を利用しやすいように 2 倍の長さで行う
prefix_sum = [0] * (2 * N + 1)
for i in range(2 * N):
    prefix_sum[i + 1] = prefix_sum[i] + W[i % N]

# q: W を何周するか,
# r: W を何周した後の残りの和
q, r = divmod(X, prefix_sum[N])
# nums[i] := i から始めた場合の X 以上を作るために必要なジャガイモの個数
nums = [0] * N
# i のペアを探す。
next_index = [0] * N
for i in range(N):
    lo, hi = i - 1, i + N
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if prefix_sum[mid] - prefix_sum[i] >= r:
            hi = mid
        else:
            lo = mid

    print(f"[DEBUG] {i=} {hi=}")
    nums[i] = q * N + (hi - i)
    next_index[i] = hi % N

# K 個のじゃがいも梱包について、W のどこから始めるかをダブリンぐで求める。
M = 60
dp = [[0] * N for _ in range(M)]
dp[0][:] = next_index[:]

for j in range(1, M):
    for i in range(N):
        dp[j][i] = dp[j - 1][dp[j - 1][i]]

for _ in range(Q):
    K = int(input()) - 1

    c = 0
    mask = 1
    for j in range(M):
        if K & mask:
            c = dp[j][c]
        mask <<= 1

    print(nums[c])
