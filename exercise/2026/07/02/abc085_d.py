# >>> atcoder-stat >>>
# started_at  = 2026-07-02T14:28:54+09:00
# solved_at   = 2026-07-02T14:42:32+09:00
# duration_ms = 818793
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

N, H = map(int, input().split())
katana = []
for i in range(N):
    a, b = map(int, input().split())
    katana.append((b, a, i))
katana.sort(reverse=True)

use_i = -1
use_a = 0
for _, a, i in katana:
    if a > use_a:
        use_a, use_i = a, i

ans = 0
for b, a, i in katana:
    if b >= use_a:
        ans += 1
        H -= b
    else:
        break
    if H <= 0:
        break
print(f"[DEBUG] {H=}")
if H > 0:
    ans += (H + use_a - 1) // use_a
print(ans)
