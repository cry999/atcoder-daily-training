# >>> atcoder-stat >>>
# started_at  = 2026-10-09T11:20:29+09:00
# solved_at   = 2026-10-09T12:02:28+09:00
# duration_ms = 2519242
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.fenwicktree import FenwickTree
import sys

input = sys.stdin.readline

N, Q = map(int, input().split())
S = input().rstrip()

bad = FenwickTree(N)
for i in range(N - 1):
    bad.add(i, int(S[i] == S[i + 1]))

for _ in range(Q):
    q, l, r = map(int, input().split())
    l -= 1
    r -= 1
    if q == 1:
        if l - 1 >= 0:
            bad.add(l - 1, 1 if not bad.sum(l - 1, l) else -1)
        bad.add(r, 1 if not bad.sum(r, r + 1) else -1)
    else:
        print("Yes" if not bad.sum(l, r) else "No")
