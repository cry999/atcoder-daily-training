# >>> atcoder-stat >>>
# started_at  = 2026-09-17T16:17:01+09:00
# solved_at   = 2026-09-17T16:21:52+09:00
# duration_ms = 291131
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList
import sys

input = sys.stdin.readline


N, M = map(int, input().split())
works = [tuple(map(int, input().split())) for _ in range(N)]
works.sort()
selectable = SortedList()
ans = 0

# d: 残り日数
i = 0
for d in range(1, M + 1):
    while i < N and works[i][0] == d:
        selectable.add(works[i][1])
        i += 1

    if selectable:
        ans += selectable.pop()
print(ans)
