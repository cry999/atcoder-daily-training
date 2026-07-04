# >>> atcoder-stat >>>
# started_at  = 2026-07-04T15:52:11+09:00
# solved_at   = 2026-07-04T16:00:59+09:00
# duration_ms = 528000
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
from collections import Counter
import sys

input = sys.stdin.readline

T = int(input())

for _ in range(T):
    S = input().rstrip()

    counter = Counter(S)
    can_use = SortedList(counter.items(), lambda x: x[1])
    stack = []

    ans = []
    while can_use:
        c, n = can_use.pop()
        ans.append(c)
        n -= 1
        if stack:
            can_use.add(stack.pop())
        if n > 0:
            stack.append((c, n))

    if len(ans) == len(S):
        print("Yes")
        print("".join(ans))
    else:
        print("No")
