# >>> atcoder-stat >>>
# started_at  = 2026-07-20T10:16:13+09:00
# solved_at   = 2026-07-20T10:20:31+09:00
# duration_ms = 258763
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.fenwicktree import FenwickTree

N = int(input())
(*A,) = map(int, input().split())
index = {a: i for i, a in enumerate(sorted(A))}

num_bit = FenwickTree(N)
sum_bit = FenwickTree(N)

ans = 0
for a in A:
    i = index[a]
    ans += num_bit.sum(0, i) * a - sum_bit.sum(0, i)
    num_bit.add(i, 1)
    sum_bit.add(i, a)
print(ans)
