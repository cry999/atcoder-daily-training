# >>> atcoder-stat >>>
# started_at  = 2026-09-11T13:13:26+09:00
# solved_at   = 2026-09-11T13:28:49+09:00
# duration_ms = 923144
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList
import sys

input = sys.stdin.readline

T = int(input())
for _ in range(T):
    N = int(input())
    balls = [tuple(map(int, input().split())) for _ in range(N)]
    balls.sort()

    def solve():
        rights = SortedList()

        i = 0
        while i < N:
            l = balls[i][0]
            while i < N and balls[i][0] == l:
                rights.add(balls[i][1])
                i += 1

            limit = balls[i][0] if i < N else 10**9 + 1
            for p in range(l, limit):
                if not rights:
                    break
                r = rights.pop(0)
                if r < p:
                    return False

        return not rights

    print("Yes" if solve() else "No")
