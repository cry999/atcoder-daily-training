# >>> atcoder-stat >>>
# started_at  = 2026-10-10T13:16:02+09:00
# solved_at   = 2026-10-10T13:23:03+09:00
# duration_ms = 421087
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
ans = []

while A > 0 and B > 0:
    # n: 次に A を並べる文字列の数
    n = comb(A + B - 1, A - 1)
    if n >= K:
        A -= 1
        ans.append("a")
    else:
        K -= n
        B -= 1
        ans.append("b")

ans.extend(["a"] * A)
ans.extend(["b"] * B)

print("".join(ans))
