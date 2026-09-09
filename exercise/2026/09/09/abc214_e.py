# >>> atcoder-stat >>>
# started_at  = 2026-09-09T09:07:37+09:00
# <<< atcoder-stat <<<
import sys
from sortedcontainers import SortedList

input = sys.stdin.readline


T = int(input())
for _ in range(T):
    N = int(input())
    sections = [tuple(map(int, input().split())) for _ in range(N)]
    sections.sort()

    def solve():
        putting = SortedList()
        next_pos = 0  # 次にボールを置いた位置
        i = 0

        while i < N:
            l, r = sections[i]
            next_pos = max(next_pos, l)
            putting.add(r)
            while i + 1 < N and sections[i + 1][0] == l:
                putting.add(sections[i + 1][1])
                i += 1

            limit = sections[i + 1][0] if i + 1 < N else 10**9 + 1
            while putting and next_pos < limit:
                if putting[0] < next_pos:
                    return False
                putting.pop(0)
                next_pos += 1

            i += 1
        return not putting

    print("Yes" if solve() else "No")
