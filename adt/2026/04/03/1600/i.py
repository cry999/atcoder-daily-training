MOD = 998244353
N, D = map(int, input().split())
(*p,) = map(int, input().split())
(*q,) = map(int, input().split())

D1 = D + 1
# dp[t][i][j]: 第t成分までの r の値が確定していて、sum{|pn-rn|} = i, sum{|qn-rn|} = j である
# 場合の数
dp = [0] * D1 * D1
dp[0] = 1

for t in range(N):
    # nxt: 第t+1成分までの r の値が確定していて、sum{|pn-rn|} = i, sum{|qn-rn|} = j である場合の数
    nxt = [0] * D1 * D1

    # 斜め方向をあらかじめ累積和で計算しておく。
    # (s, 0), (s-1, 1), ... (1, s-1), (0, s)
    dp2 = [0] * D1 * D1
    for i in range(D1):
        for j in range(D1):
            dp2[i * D1 + j] = dp[i * D1 + j]
            if 0 <= i - 1 and j + 1 <= D:
                dp2[i * D1 + j] += dp2[(i - 1) * D1 + (j + 1)]
                dp2[i * D1 + j] %= MOD

    # (i+1, j+1), (i+2, j+2), ...
    dp3 = [0] * D1 * D1
    for i in range(D1):
        for j in range(D1):
            dp3[i * D1 + j] = dp[i * D1 + j]
            if i - 1 >= 0 and j - 1 >= 0:
                dp3[i * D1 + j] += dp3[(i - 1) * D1 + (j - 1)]
                dp3[i * D1 + j] %= MOD

    s = abs(p[t] - q[t])
    # (|p[t] - r|, |q[t] - r|) の組は、s = |p[t] - q[t]| を用いて、
    #   (2D, 2D-s), (2D-1, 2D-s-1), ..., (s+2, 2), (s+1, 1),
    #   (s, 0), (s-1, 1), ..., (1, s-1), (0, s),
    #   (1, s+1), (2, s+2), ..., (2D-s-1, 2D-1), (2D-s, 2D)
    # となる。これらを事前に計算した累積和を用いて計算する。

    for i in range(D1):
        for j in range(D1):
            # 遷移後の距離合計の組が (i, j) となるのは
            # (i-s, j), (i-s+1, j-1), ..., (i-1, j-s+1), (i, j-s)
            # である。これらの累積和を dp2 から計算する。
            si, sj = i, j - s
            if sj < 0:
                si, sj = si + sj, 0
            if 0 <= si <= D and 0 <= sj <= D:
                nxt[i * D1 + j] += dp2[si * D1 + sj]
                nxt[i * D1 + j] %= MOD
            ti, tj = i - (s + 1), j + 1
            if 0 <= ti <= D and 0 <= tj <= D:
                nxt[i * D1 + j] -= dp2[ti * D1 + tj]
                nxt[i * D1 + j] %= MOD

    for i in range(D1):
        for j in range(D1):
            if i + 1 <= D and j + s + 1 <= D:
                nxt[(i + 1) * D1 + (j + s + 1)] += dp3[i * D1 + j]
                nxt[(i + 1) * D1 + (j + s + 1)] %= MOD
            if i + s + 1 <= D and j + 1 <= D:
                nxt[(i + s + 1) * D1 + (j + 1)] += dp3[i * D1 + j]
                nxt[(i + s + 1) * D1 + (j + 1)] %= MOD

    dp = nxt

print(sum(dp) % MOD)
