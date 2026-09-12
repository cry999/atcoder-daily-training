# >>> atcoder-stat >>>
# started_at  = 2026-09-12T16:56:38+09:00
# solved_at   = 2026-09-12T17:10:05+09:00
# duration_ms = 780000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
INF = float("inf")


N = int(input())
(*A,) = map(int, input().split())

# 平均値

# 1. sum(A) / N を X 以上にできるか?
# 2. sum(A-X) / N を 0 以上にできるか?
# 3. DP で解く

# dp[i][s] := A[0] ~ A[i] までの選択状況を確定した上で、A[i] の選択状況が s である場合の選択された A[i]-X の総和の最大値
dp = [0, 0]

lo, hi = 0, 10**9 + 1
EPS = 1e-6
while hi - lo > EPS:
    x = (hi + lo) / 2

    dp = [0, 0]

    for i in range(N):
        dp[:] = [
            # A[i] を選ばない場合: A[i-1] は選んでないといけない
            dp[1],
            # A[i] を選ぶ場合: A[i-1] はどっちでもいい
            max(dp) + A[i] - x,
        ]

    if max(dp) >= 0:
        lo = x
    else:
        hi = x

print(lo)

# 中央値

# 1. 全体で M 個選択して X 以上の値を過半数にできるか?
# 2. X 以上の値は問答無用で選択していい。
# 3. X 未満の値は最低限をとる
# 4. 最低限の選択は、1 つまえの要素が選択されていない場合だけ取得する。

lo, hi = 0, 10**9 + 1
while hi - lo > 1:
    x = (hi + lo) // 2

    selected = [a >= x for a in A]

    for i in range(1, N):
        if not selected[i - 1] and not selected[i]:
            selected[i] = True

    cnt_over = sum(a >= x for a in A)
    cnt_under = sum(selected) - cnt_over
    if cnt_under < cnt_over:
        lo = x
    else:
        hi = x

print(lo)
