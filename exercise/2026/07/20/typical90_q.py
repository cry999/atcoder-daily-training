# >>> atcoder-stat >>>
# started_at  = 2026-07-20T11:16:56+09:00
# solved_at   = 2026-07-20T11:35:24+09:00
# duration_ms = 1108586
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.fenwicktree import FenwickTree
import sys

input = sys.stdin.readline

N, M = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]
edges.sort()  # l の昇順

bit = FenwickTree(N + 1)

ans = 0
# l が同じ場合の一時退避場所
stack = []
prev_l = 0
for l, r in edges:
    if prev_l != l:
        while stack:
            bit.add(stack.pop(), 1)

    ans += bit.sum(l + 1, r)
    print(f"[DEBUG] {l=} {r=} {ans=}")
    stack.append(r)
    prev_l = l
print(ans)
