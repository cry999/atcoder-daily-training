# >>> atcoder-stat >>>
# started_at  = 2026-10-03T14:18:25+09:00
# solved_at   = 2026-10-03T14:21:46+09:00
# duration_ms = 201630
# ac          = true
# editorial   = true
# knowledge   = 1
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import functools
import sys

input = sys.stdin.readline


M = 100
T = int(input())
for _ in range(T):
    N = int(input())
    seg = [tuple(map(int, input().split())) for _ in range(N)]
    seg.sort()

    @functools.cache
    def dp(l: int, r: int):
        if l >= r:
            return 0

        reachable = {dp(l, sl) ^ dp(sr, r) for sl, sr in seg if l <= sl and sr <= r}
        g = 0
        while g in reachable:
            g += 1
        return g

    print("Alice" if dp(0, 100) else "Bob")
