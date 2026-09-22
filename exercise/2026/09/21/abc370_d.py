# >>> atcoder-stat >>>
# started_at  = 2026-09-21T10:21:52+09:00
# solved_at   = 2026-09-21T10:33:15+09:00
# duration_ms = 683199
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
from sortedcontainers import SortedList

input = sys.stdin.readline


H, W, Q = map(int, input().split())

walls_by_row = [SortedList(range(W)) for _ in range(H)]
walls_by_col = [SortedList(range(H)) for _ in range(W)]

ans = H * W
for _ in range(Q):
    r, c = map(int, input().split())
    r, c = r - 1, c - 1
    print(f"[DEBUG] query: {r=} {c=}")

    i = walls_by_row[r].bisect_left(c)
    if i < len(walls_by_row[r]) and walls_by_row[r][i] == c:
        # 壁がまだ残っている場合、それを除去する
        walls_by_row[r].remove(c)
        walls_by_col[c].remove(r)
        print(f"[DEBUG] ==> remove {(r, c)=}")
        ans -= 1
    else:
        # すでに破壊されている場合は、最も近い上下左右の壁を破壊する。
        i = walls_by_row[r].bisect_left(c)
        if i < len(walls_by_row[r]):
            right: int = walls_by_row[r].pop(i)
            print(f"[DEBUG] ==> remove right {(r, right)=}")
            walls_by_col[right].remove(r)
            ans -= 1
        if i - 1 >= 0:
            left: int = walls_by_row[r].pop(i - 1)
            print(f"[DEBUG] ==> remove left {(r, left)=}")
            walls_by_col[left].remove(r)
            ans -= 1

        i = walls_by_col[c].bisect_left(r)
        if i < len(walls_by_col[c]):
            down: int = walls_by_col[c].pop(i)
            print(f"[DEBUG] ==> remove down {(down, c)=}")
            walls_by_row[down].remove(c)
            ans -= 1
        if i - 1 >= 0:
            up: int = walls_by_col[c].pop(i - 1)
            print(f"[DEBUG] ==> remove up {(up, c)=}")
            walls_by_row[up].remove(c)
            ans -= 1
print(ans)
