# >>> atcoder-stat >>>
# started_at  = 2026-11-24T10:41:15+09:00
# solved_at   = 2026-11-24T11:08:23+09:00
# duration_ms = 1628929
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList

N, Q = map(int, input().split())
s = SortedList()
s.add((N, 1))

ans = N
for _ in range(Q):
    l, r = map(int, input().split())
    i = s.bisect_left((l, 0))
    while i < len(s) and s[i][1] <= r:
        rr, ll = s[i]
        if l < ll:
            if rr <= r:
                # 完全に含まれる場合は削除
                _ = s.pop(i)
                ans -= rr - ll + 1
            elif ll <= r:
                # 右側がはみ出る場合は右側を残す
                s.pop(i)
                s.add((rr, r + 1))
                ans -= r - ll + 1
                break
            else:
                # あり得ない
                pass
        elif ll <= l <= rr:
            if rr <= r:
                # 左側がはみ出る場合は左側を残す
                s.pop(i)
                s.add((l - 1, ll))
                ans -= rr - l + 1
                i += 1
            elif ll <= r:
                # 左右がはみ出る場合は両側を残す
                s.pop(i)
                s.add((l - 1, ll))
                s.add((rr, r + 1))
                ans -= r - l + 1
                break
        else:
            break
    print(f"[DEBUG] {s=}")
    print(ans)
