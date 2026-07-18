# >>> atcoder-stat >>>
# started_at  = 2026-07-17T19:33:28+09:00
# solved_at   = 2026-07-17T19:50:31+09:00
# duration_ms = 1023743
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedDict

T = int(input())

for _ in range(T):
    N, X = map(int, input().split())
    (*A,) = map(int, input().split())

    queue = SortedDict()
    queue[X] = 1
    ans = 0
    for a in A:
        while queue.peekitem(-1)[0] >= a:
            x, n = queue.popitem()
            q, r = divmod(x, a)
            ans += q * n
            queue[a - 1] = queue.get(a - 1, 0) + q * n
            if r:
                queue[r] = queue.get(r, 0) + n

    print(ans)
