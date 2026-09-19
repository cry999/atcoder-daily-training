# >>> atcoder-stat >>>
# started_at  = 2026-09-18T11:45:01+09:00
# solved_at   = 2026-09-18T12:40:26+09:00
# duration_ms = 3325717
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys
from atcoder.segtree import SegTree

input = sys.stdin.readline


H, W, N = map(int, input().split())
points = [tuple(map(int, input().split())) for _ in range(N)]
points.sort()

# r の小さい順に見ながら c 以下の最大値を segtree で管理する。
seg = SegTree(max, 0, W + 1)

# 復元用に、スコアごとに位置を管理する
points_by_score = [[] for _ in range(N + 1)]

for r, c in points:
    score = seg.prod(0, c + 1)
    seg.set(c, score + 1)
    points_by_score[score + 1].append((r, c))

max_score = seg.all_prod()
trace = []
score = max_score
cr, cc = H, W
while score > 0:
    for r, c in points_by_score[score]:
        if r <= cr and c <= cc:
            trace.append((r, c))
            cr, cc = r, c
            break
    score -= 1

trace.reverse()
trace.append((H, W))

cr, cc = 1, 1
ans = []
for r, c in trace:
    ans.append("D" * (r - cr))
    ans.append("R" * (c - cc))
    cr, cc = r, c


print(max_score)
print("".join(ans))
