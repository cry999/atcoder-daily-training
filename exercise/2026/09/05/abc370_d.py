# >>> atcoder-stat >>>
# started_at  = 2026-09-05T09:54:24+09:00
# solved_at   = 2026-09-05T10:02:25+09:00
# duration_ms = 481745
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList
import sys

input = sys.stdin.readline


H, W, Q = map(int, input().split())
rows_by_col = [SortedList(range(H)) for _ in range(W)]
cols_by_row = [SortedList(range(W)) for _ in range(H)]
ans = H * W
for _ in range(Q):
    r, c = map(int, input().split())
    r -= 1
    c -= 1

    if r in rows_by_col[c]:
        # (r, c) がまだ爆破されていないなら (r, c) のみ爆破
        rows_by_col[c].remove(r)
        cols_by_row[r].remove(c)
        ans -= 1
    else:
        # (r, c) が爆破済みなら、上下左右の壁を破壊

        # 上下方向
        i = rows_by_col[c].bisect_left(r)
        if i < len(rows_by_col[c]):
            rr: int = rows_by_col[c].pop(i)
            cols_by_row[rr].remove(c)
            ans -= 1
        if i > 0:
            rr: int = rows_by_col[c].pop(i - 1)
            cols_by_row[rr].remove(c)
            ans -= 1

        # 左右方向
        i = cols_by_row[r].bisect_left(c)
        if i < len(cols_by_row[r]):
            cc: int = cols_by_row[r].pop(i)
            rows_by_col[cc].remove(r)
            ans -= 1
        if i > 0:
            cc: int = cols_by_row[r].pop(i - 1)
            rows_by_col[cc].remove(r)
            ans -= 1
print(ans)
