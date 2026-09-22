# >>> atcoder-stat >>>
# started_at  = 2026-09-22T02:33:26+09:00
# solved_at   = 2026-09-22T02:41:16+09:00
# duration_ms = 470851
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers.sortedlist import SortedList
import sys

input = sys.stdin.readline


def solve():
    N = int(input())

    balls = [tuple(map(int, input().split())) for _ in range(N)]
    balls.sort()

    rights = SortedList()
    i = 0
    while i < N:
        print(f"[DEBUG] {i=}")
        l = balls[i][0]
        while i < N and balls[i][0] == l:
            rights.add(balls[i][1])
            i += 1

        limit = balls[i][0] if i < N else 10**9 + 1
        print(f"[DEBUG] {l=}, {limit=}, {rights=}")
        for at in range(l, limit):
            if not rights:
                break
            if rights[0] < at:
                return False
            print(f"[DEBUG] put {rights[0]} at {at}")
            rights.pop(0)  # at に置く

    return not rights


T = int(input())
for _ in range(T):
    if solve():
        print("Yes")
    else:
        print("No")
