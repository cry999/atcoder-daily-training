# >>> atcoder-stat >>>
# started_at  = 2026-07-04T20:32:17+09:00
# solved_at   = 2026-07-04T20:39:50+09:00
# duration_ms = 453404
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K = map(int, input().split())
(*A,) = map(int, input().split())

INF = 10**25

lo, hi = 0, INF
while hi - lo > 1:
    mid = (lo + hi) // 2

    # 全ての i について A[i] を mid 以上にできるか？
    op = 0
    for i in range(N):
        d = mid - A[i]
        if d <= 0:
            continue
        op += (d + i) // (i + 1)

    if op <= K:
        lo = mid
    else:
        hi = mid

print(lo)
