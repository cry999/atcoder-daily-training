# >>> atcoder-stat >>>
# started_at  = 2026-09-29T13:05:00+09:00
# solved_at   = 2026-09-29T13:42:12+09:00
# duration_ms = 2232667
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


T = int(input())
for _ in range(T):
    a, s = map(int, input().split())
    x, y = 0, 0
    carry = 0

    for i in range(61):
        b = 1 << i
        print(f"[DEBUG] === {i=} ===")
        print(f"[DEBUG] {b=:060b} ({carry=})")
        print(f"[DEBUG] {a=:060b}")
        print(f"[DEBUG] {s=:060b}")
        if a & b:
            if bool(s & b) != bool(carry):
                x, y = -1, -1
                break
            x |= b
            y |= b
            carry = 1
        else:
            if not s & b and not carry:
                print(f"[DEBUG] not not")
                x |= 0
                y |= 0
                carry = 0
            elif not s & b and carry:
                print(f"[DEBUG] not ok")
                x |= 0
                y |= b
                carry = 1
            elif s & b and not carry:
                print(f"[DEBUG] ok not")
                x |= 0
                y |= b
                carry = 0
            else:
                print(f"[DEBUG] ok ok")
                x |= 0
                y |= 0
                carry = 0
        print(f"[DEBUG] {x=:060b}")
        print(f"[DEBUG] {y=:060b}")

    if x >= 0 and y >= 0 and x + y == s and x & y == a:
        print("Yes")
    else:
        print("No")
