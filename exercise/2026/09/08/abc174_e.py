# >>> atcoder-stat >>>
# started_at  = 2026-09-08T10:58:07+09:00
# solved_at   = 2026-09-08T11:02:31+09:00
# duration_ms = 264883
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

# K 回の操作で、A の要素を全て X 以下にできるかを二分探索する。

lo, hi = 0, max(A)
while hi - lo > 1:
    X = (lo + hi) // 2

    op = 0
    for a in A:
        op += (a - 1) // X

    if op <= K:
        hi = X
    else:
        lo = X
print(hi)
