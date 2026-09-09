# >>> atcoder-stat >>>
# started_at  = 2026-09-09T08:08:20+09:00
# solved_at   = 2026-09-09T08:28:56+09:00
# duration_ms = 1236027
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


# 平均値
# 1. 平均値を X 以上にできるか?
# 2. 平均値が X 以上: sum(A) / N >= X -> sum(A - X) / N >= 0
# 3. なので、条件を満たすように、sum(A - X) >= 0 となる A の部分列を構成できるかをみる。
# 4. X を二分探索で求める。

lo, hi = 0, max(A) + 1
EPS = 1e-6
while hi - lo > EPS:
    x = (lo + hi) / 2

    # 連続して選ばれていない部分はどうやって選択する?
    # dp で最大になるように選ぼう。
    # dp[i][s] := i 番目までを条件を選ぶように選んだ時に i 番目の選択状況が s である時の sum(A-X) の最大値

    dp = [0, 0]
    for i in range(N):
        dp[:] = [
            # i 番目を選ばない場合は、i-1 番目を選んでいる必要がある
            dp[1],
            # i 番目を選ぶ場合は、i-1 番目を選んでいない場合の最大値に A[i]-x を足す
            max(dp[0], dp[1]) + A[i] - x,
        ]

    if max(dp) >= 0:
        lo = x
    else:
        hi = x
avg = lo
print(avg)

# 中央値
# 1. 中央値を X 以上にできるか?
# 2. 部分列の条件を満たしながら、X 以上の要素を ceil(M/2) (M は部分列の長さ) 個以上取得できるか
# 3. X 以上の要素を ceil(M/2) 個以上取得するには?
# 4. とりあえず X 以上の要素を全部とる。
# 5. その後、X 未満の要素を最小限とる。
# 6. 最小限の取り方は左から見ていって、一つ左も自分も未選択なら自分を選択する、で大丈夫なはず

lo, hi = 0, max(A) + 1
while hi - lo > 1:
    x = (lo + hi) // 2

    selected = [a >= x for a in A]
    for i in range(1, N):
        if selected[i - 1] or selected[i]:
            continue
        selected[i] = True

    sum_over = sum(a >= x for a in A)
    sum_selected = sum(selected)
    if sum_selected - sum_over < sum_over:
        lo = x
    else:
        hi = x

median = lo
print(median)
