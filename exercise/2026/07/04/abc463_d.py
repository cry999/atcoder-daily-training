# >>> atcoder-stat >>>
# started_at  = 2026-07-04T11:52:09+09:00
# solved_at   = 2026-07-04T11:52:16+09:00
# duration_ms = 600000
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
clothes = [tuple(map(int, input().split())) for _ in range(N)]
clothes.sort(key=lambda x: x[1])

lo, hi = 0, 10**9 + 1
while hi - lo > 1:
    mid = (lo + hi) // 2

    selected_r = -(10**18)
    cnt = 0
    for l, r in clothes:
        if selected_r + mid <= l:
            cnt += 1
            selected_r = r

    if cnt >= K:
        lo = mid
    else:
        hi = mid

print(lo if lo > 0 else -1)
