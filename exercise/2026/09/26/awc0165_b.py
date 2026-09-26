# >>> atcoder-stat >>>
# started_at  = 2026-09-26T17:04:40+09:00
# solved_at   = 2026-09-26T17:06:50+09:00
# duration_ms = 130105
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


N = int(input())
cur = 0
seq = 0
ans = 0
for _ in range(N):
    a = int(input())
    if cur <= a:
        seq += 1
    else:
        ans = max(ans, seq)
        seq = 1
    cur = a
print(max(ans, seq))
