# >>> atcoder-stat >>>
# started_at  = 2026-09-30T08:43:36+09:00
# solved_at   = 2026-09-30T08:56:44+09:00
# duration_ms = 788238
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

input = sys.stdin.readline


T = int(input())
for _ in range(T):
    a, s = map(int, input().split())
    x, y, c = 0, 0, 0

    for i in range(60):
        b = 1 << i
        print(f"[DEBUG] {bool(a & b)}, {bool(s & b)}")
        if a & b and s & b:
            if not c:
                x = y = -1
                break
            x |= b
            y |= b
            c = 1
        elif a & b:
            if c:
                x = y = -1
                break
            x |= b
            y |= b
            c = 1
        elif s & b:
            if c:
                x |= 0
                y |= 0
                c = 0
            else:
                x |= 0
                y |= b
                c = 0
        else:
            if c:
                x |= 0
                y |= b
                c = 1
            else:
                x |= 0
                y |= 0
                c = 0

    print(f"[DEBUG] {x=}, {y=}, {c=}")
    if x < 0:
        print("No")
    elif x + y == s and x & y == a and not c:
        print("Yes")
    else:
        print("No")
