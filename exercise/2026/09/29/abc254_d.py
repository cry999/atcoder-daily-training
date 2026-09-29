# >>> atcoder-stat >>>
# started_at  = 2026-09-29T13:42:22+09:00
# solved_at   = 2026-09-29T14:19:24+09:00
# duration_ms = 2222795
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from collections import defaultdict
import math

N = int(input())

f = [0] * (N + 1)
for i in range(1, math.ceil(math.sqrt(N)) + 1):
    n = i * i
    for j in range(n, N + 1):
        if j % n == 0:
            f[j] = n

c = defaultdict(int)
for i in range(1, N + 1):
    c[i // f[i]] += 1

ans = 0
for v in c.values():
    ans += v * v
print(ans)
