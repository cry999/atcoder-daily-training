# >>> atcoder-stat >>>
# started_at  = 2026-09-02T15:15:34+09:00
# solved_at   = 2026-09-02T15:48:08+09:00
# duration_ms = 1954951
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList
import sys

input = sys.stdin.readline

H, W, Q = map(int, input().split())
ans = H * W

cols_by_row = [SortedList(range(W)) for _ in range(H)]
rows_by_col = [SortedList(range(H)) for _ in range(W)]

for _ in range(Q):
    row, col = map(int, input().split())
    row, col = row - 1, col - 1
    pos = row * W + col

    if col in cols_by_row[row]:
        ans -= 1
        cols_by_row[row].remove(col)
        rows_by_col[col].remove(row)
    else:
        i = cols_by_row[row].bisect_left(col)
        if i < len(cols_by_row[row]):
            c = cols_by_row[row].pop(i)
            rows_by_col[c].remove(row)
            ans -= 1
        if i > 0:
            c = cols_by_row[row].pop(i - 1)
            rows_by_col[c].remove(row)
            ans -= 1

        i = rows_by_col[col].bisect_left(row)
        if i < len(rows_by_col[col]):
            r = rows_by_col[col].pop(i)
            cols_by_row[r].remove(col)
            ans -= 1
        if i > 0:
            r = rows_by_col[col].pop(i - 1)
            cols_by_row[r].remove(col)
            ans -= 1


print(ans)
