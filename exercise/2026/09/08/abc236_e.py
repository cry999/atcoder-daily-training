# >>> atcoder-stat >>>
# started_at  = 2026-09-08T11:24:34+09:00
# solved_at   = 2026-09-08T12:08:50+09:00
# duration_ms = 2656389
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())

# 平均値
lo, hi = 0, max(A)
EPS = 1e-6
while hi - lo > EPS:
    X = (lo + hi) / 2
    # 平均値が X 以上になるかを判定する。
    # 1. sum(A[i] - X) >= 0 となるように条件を満たす取り方があるか？
    dp = [0, A[0] - X]  # i 番目を選択 [しなかった, した] 時の和の最大値
    for i in range(1, N):
        dp[:] = [dp[1], max(dp) + A[i] - X]
        print(f"[DEBUG] {X=}: {dp=}")

    if max(dp) >= 0:
        lo = X
    else:
        hi = X
avg = lo
print(avg)


# 中央値
lo, hi = 0, max(A) + 1
while hi - lo > 1:
    X = (lo + hi) // 2
    # 中央値が X 以上になるかを判定する
    # 1. X 以上の値をとりあえず全部とる
    # 2. 条件を満たすように、最小限の X 未満の値をとる
    selected = [a >= X for a in A]

    sum_over = sum(selected)

    for i in range(1, N):
        if not selected[i] and not selected[i - 1]:
            selected[i] = True

    sum_all = sum(selected)

    if sum_all - sum_over < sum_over:
        lo = X
    else:
        hi = X

median = lo
print(median)
