# >>> atcoder-stat >>>
# started_at  = 2026-09-08T15:18:09+09:00
# solved_at   = 2026-09-08T15:46:34+09:00
# duration_ms = 1705978
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
import sys
from sortedcontainers import SortedList

input = sys.stdin.readline


T = int(input())
for _ in range(T):
    N = int(input())

    events = []
    for _ in range(N):
        l, r = map(int, input().split())
        events.append((l, r))
    events.sort()

    can_use = SortedList()

    def solve():
        i = 0
        while i < N:
            l, r = events[i]
            can_use.add(r)
            while i + 1 < N and events[i + 1][0] == l:
                can_use.add(events[i + 1][1])
                i += 1

            M = events[i + 1][0] if i + 1 < N else 10**9 + 1
            cur = l
            while cur < M and can_use:
                if can_use[0] < cur:
                    return False
                can_use.pop(0)
                cur += 1

            i += 1
        return not can_use

    print("Yes" if solve() else "No")
