# >>> atcoder-stat >>>
# started_at  = 2026-09-17T16:50:48+09:00
# solved_at   = 2026-09-17T16:59:57+09:00
# duration_ms = 549218
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys
from sortedcontainers import SortedList

input = sys.stdin.readline

T = int(input())
for _ in range(T):
    N, K = map(int, input().split())
    (*A,) = map(int, input().split())
    (*B,) = map(int, input().split())

    C = sorted(zip(B, A))
    target = SortedList()
    sum_b = 0
    INF = 10**20
    ans = INF
    for b, a in C:
        if len(target) == K:
            _, prev_b = target.pop()
            sum_b -= prev_b

        target.add((a, b))
        sum_b += b

        if len(target) == K:
            max_a = target[-1][0]
            ans = min(ans, max_a * sum_b)
    print(ans)
