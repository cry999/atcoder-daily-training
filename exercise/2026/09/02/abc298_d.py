# >>> atcoder-stat >>>
# started_at  = 2026-09-02T15:03:25+09:00
# solved_at   = 2026-09-02T15:10:17+09:00
# duration_ms = 412545
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from collections import deque
import sys

input = sys.stdin.readline

S = 1
numbers = deque([1])
MOD = 998244353


Q = int(input())

pow10 = 1
inv10 = pow(10, MOD - 2, MOD)
for q in range(Q):
    query, *args = map(int, input().split())

    if query == 1:
        x = args[0]
        S = (S * 10 + x) % MOD
        numbers.append(x)
        pow10 = pow10 * 10 % MOD
    elif query == 2:
        n = numbers.popleft()
        ex = n * pow10 % MOD
        S = (S - ex) % MOD
        pow10 = pow10 * inv10 % MOD
    else:  # query == 3
        print(S)
