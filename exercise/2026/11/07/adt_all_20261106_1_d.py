# >>> atcoder-stat >>>
# started_at  = 2026-11-07T07:15:30+09:00
# solved_at   = 2026-11-07T07:20:29+09:00
# duration_ms = 299635
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from collections import Counter


N, M = map(int, input().split())
(*A,) = map(int, input().split())

counter = Counter(A)

ans = 0
while len(counter) == M:
    ans += 1
    a = A.pop()
    counter[a] -= 1
    if counter[a] == 0:
        del counter[a]
print(ans)
