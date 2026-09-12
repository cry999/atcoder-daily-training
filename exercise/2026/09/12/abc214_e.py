# >>> atcoder-stat >>>
# started_at  = 2026-09-12T17:46:18+09:00
# solved_at   = 2026-09-12T17:57:11+09:00
# duration_ms = 653848
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from heapq import heappop
from heapq import heappush
import sys

input = sys.stdin.readline

MAX_LIMIT = 10**9


def solve(balls: list[tuple[int, int]]):
    N = len(balls)

    i = 0
    rights = []
    while i < N:
        l, _ = balls[i]
        print(f"[DEBUG] === {i=} {l=}")
        while i < N and balls[i][0] == l:
            heappush(rights, balls[i][1])
            i += 1

        limit = balls[i][0] if i < N else MAX_LIMIT + 1
        for pos in range(l, limit):
            if not rights:
                break
            r = heappop(rights)
            print(f"[DEBUG] {pos=}, {r=}, {rights=}")
            if r < pos:
                return False

    return not rights


ANS = ["No", "Yes"]

T = int(input())
for _ in range(T):
    N = int(input())
    balls = [tuple(map(int, input().split())) for _ in range(N)]
    balls.sort()

    print(ANS[solve(balls)])
