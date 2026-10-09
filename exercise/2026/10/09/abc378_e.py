# >>> atcoder-stat >>>
# started_at  = 2026-10-09T12:05:34+09:00
# solved_at   = 2026-10-09T12:35:05+09:00
# duration_ms = 1771502
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.fenwicktree import FenwickTree

N, M = map(int, input().split())
(*A,) = map(int, input().split())

bit = FenwickTree(M)
bit.add(0, 1)

p = 0
sum_p = 0
ans = 0

for r, a in enumerate(A, 1):
    p = (p + a) % M

    ans += r * p - sum_p + M * bit.sum(p + 1, M)  # p < x < M
    bit.add(p, 1)
    sum_p += p
print(ans)
