# >>> atcoder-stat >>>
# started_at  = 2026-09-22T01:49:14+09:00
# solved_at   = 2026-09-22T01:58:45+09:00
# duration_ms = 571140
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<

N = int(input())
(*A,) = map(int, input().split())

INF = float("inf")

# 平均値
# 1. sum(A[i]) / M >= X となるか?
# 2. 1 を変形して sum(A[i] - X) >= 0 となるか? を考える。
# 3. DP で解くことができる。

lo, hi = 0, 10**9 + 1
EPS = 1e-6
while hi - lo > EPS:
    x = (lo + hi) / 2

    dp = [0, 0]
    for i in range(N):
        dp = [
            # i 番目を選ばない場合は、i-1 番目は選んでいる必要がある。
            dp[1],
            # i 番目を選ぶ場合は、i-1 番目はどっちでもいい。
            max(dp) + A[i] - x,
        ]

    if max(dp) >= 0:
        lo = x
    else:
        hi = x

avg = lo
print(avg)


# 中央値
# 1. X 以上の値を過半数選べるか?
# 2. 貪欲法。A[i] >= X の値は全て選ぶ。
# 3. 残りは条件を満たす最低限だけを選ぶ。

lo, hi = 0, 10**9 + 1
while hi - lo > 1:
    x = (lo + hi) // 2

    selected = [a >= x for a in A]
    num_over = sum(selected)
    for i in range(N - 1):
        if selected[i + 1]:
            continue

        if not selected[i] and not selected[i + 1]:
            selected[i + 1] = True

    num_selected = sum(selected)
    num_under = num_selected - num_over
    if num_under < num_over:
        lo = x
    else:
        hi = x

median = lo
print(median)
