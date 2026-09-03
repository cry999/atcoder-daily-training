# >>> atcoder-stat >>>
# started_at  = 2026-09-04T05:01:15+09:00
# solved_at   = 2026-09-04T05:06:56+09:00
# duration_ms = 341313
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

cols_by_row = [SortedList(range(W)) for _ in range(H)]
rows_by_col = [SortedList(range(H)) for _ in range(W)]

ans = H * W
for _ in range(Q):
    r, c = map(int, input().split())
    r -= 1
    c -= 1

    if c in cols_by_row[r]:
        # 爆破されていない
        cols_by_row[r].remove(c)
        rows_by_col[c].remove(r)

        ans -= 1
    else:
        # 爆破済み。上下左右を破壊する

        i = cols_by_row[r].bisect_left(c)
        if i < len(cols_by_row[r]):
            cc = cols_by_row[r].pop(i)
            rows_by_col[cc].remove(r)
            ans -= 1
        if i - 1 >= 0:
            cc = cols_by_row[r].pop(i - 1)
            rows_by_col[cc].remove(r)
            ans -= 1

        i = rows_by_col[c].bisect_left(r)
        if i < len(rows_by_col[c]):
            rr = rows_by_col[c].pop(i)
            cols_by_row[rr].remove(c)
            ans -= 1
        if i - 1 >= 0:
            rr = rows_by_col[c].pop(i - 1)
            cols_by_row[rr].remove(c)
            ans -= 1

print(ans)
