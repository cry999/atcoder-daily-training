# >>> atcoder-stat >>>
# started_at  = 2026-10-03T11:27:19+09:00
# solved_at   = 2026-10-03T11:35:32+09:00
# duration_ms = 493438
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
        if not a & b and not s & b:
            y |= c
            c <<= 1
        elif not a & b:
            if not c:
                y |= b
            c = 0
        elif s & b != c:
            print("No")
            break
        else:
            x |= b
            y |= b
            c = b << 1
    else:
        if c or x + y != s or x & y != a:
            print("No")
        else:
            print("Yes")
