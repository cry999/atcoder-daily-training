# >>> atcoder-stat >>>
# started_at  = 2026-07-06T17:08:12+09:00
# solved_at   = 2026-07-06T17:12:53+09:00
# duration_ms = 281274
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from itertools import permutations

n = int(input())
(*p,) = map(int, input().split())
(*q,) = map(int, input().split())

i = 0
a, b = -1, -1
for perm in permutations(range(1, n + 1)):
    for j in range(n):
        if p[j] != perm[j]:
            break
    else:
        a = i

    for j in range(n):
        if q[j] != perm[j]:
            break
    else:
        b = i

    i += 1

assert a != -1
assert b != -1

print(abs(a - b))
