# >>> atcoder-stat >>>
# started_at  = 2026-08-07T15:23:57+09:00
# solved_at   = 2026-08-07T15:31:47+09:00
# duration_ms = 470509
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from math import comb

A, B, K = map(int, input().split())

ans = ""
cur = 0
for _ in range(A + B):
    if A == 0:
        ans += "b"
    elif B == 0:
        ans += "a"
    else:
        k = comb(A + B - 1, B)
        print(f"[DEBUG] {cur=} {k=}")
        if K <= cur + k:
            ans += "a"
            A -= 1
        else:
            ans += "b"
            B -= 1
            cur += k
print(ans)
