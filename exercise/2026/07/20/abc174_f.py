# >>> atcoder-stat >>>
# started_at  = 2026-07-20T10:26:48+09:00
# solved_at   = 2026-07-20T10:44:59+09:00
# duration_ms = 1091832
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
from atcoder.fenwicktree import FenwickTree

input = sys.stdin.readline

N, Q = map(int, input().split())
(*C,) = map(int, input().split())
# last_index[c] := 色 c の最後に登場した位置を記録する。
# r を昇順に処理すると、最後に登場した位置が範囲に入っていればそれ以前の位置は
# 入っていてもいなくても答えに影響しないし、最後に登場した位置が範囲に入ってい
# ないなら当然それ以前の登場も範囲外なので、最後に登場した位置だけ覚えていれば
# よい
last_index = [-1] * (N + 1)

query = []
for i in range(Q):
    l, r = map(int, input().split())
    query.append((r, l, i))
query.sort()

bit = FenwickTree(N)
ans = [0] * Q
j = 0
for r, l, i in query:
    while j < r:
        c = C[j]
        if last_index[c] >= 0:
            bit.add(last_index[c], -1)
        last_index[c] = j
        bit.add(j, 1)
        j += 1
    ans[i] = bit.sum(l - 1, r)
print("\n".join(map(str, ans)))
