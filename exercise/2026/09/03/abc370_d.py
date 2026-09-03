# >>> atcoder-stat >>>
# started_at  = 2026-09-03T14:03:12+09:00
# solved_at   = 2026-09-03T14:23:48+09:00
# duration_ms = 1236432
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
from sortedcontainers import SortedList
import sys

input = sys.stdin.readline


H, W, Q = map(int, input().split())

rows_by_col = [SortedList(range(H)) for _ in range(W)]
cols_by_row = [SortedList(range(W)) for _ in range(H)]

remain = H * W
for _ in range(Q):
    r, c = map(int, input().split())
    r -= 1
    c -= 1

    i = rows_by_col[c].bisect_left(r)
    print(f"[DEBUG] {r=}, {c=}, {i=}")
    print(f"[DEBUG] {rows_by_col=}")
    print(f"[DEBUG] {cols_by_row=}")

    if r in rows_by_col[c] and c in cols_by_row[r]:
        # まだ爆破されていない
        rows_by_col[c].remove(r)
        cols_by_row[r].remove(c)
        print(f"[DEBUG] removed {r=}, {c=}")
        remain -= 1
    else:
        # すでに (r, c) は爆破されている

        # 縦方向の上下を爆破する
        i = rows_by_col[c].bisect_left(r)
        if i < len(rows_by_col[c]):
            rr = rows_by_col[c].pop(i)
            cols_by_row[rr].remove(c)
            print(f"[DEBUG] removed {rr=}, {c=}")
            remain -= 1
        if i - 1 >= 0:
            rr = rows_by_col[c].pop(i - 1)
            cols_by_row[rr].remove(c)
            print(f"[DEBUG] removed {rr=}, {c=}")
            remain -= 1

        # 横方向の左右を爆破
        i = cols_by_row[r].bisect_left(c)
        if i < len(cols_by_row[r]):
            cc = cols_by_row[r].pop(i)
            rows_by_col[cc].remove(r)
            print(f"[DEBUG] removed {r=}, {cc=}")
            remain -= 1
        if i - 1 >= 0:
            cc = cols_by_row[r].pop(i - 1)
            rows_by_col[cc].remove(r)
            print(f"[DEBUG] removed {r=}, {cc=}")
            remain -= 1

print(remain)
