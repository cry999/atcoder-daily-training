# >>> atcoder-stat >>>
# started_at  = 2026-10-02T14:06:14+09:00
# solved_at   = 2026-10-02T15:10:22+09:00
# duration_ms = 3848697
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
    def dp(l: int, r: int) -> int:
        """[l, r) に完全に含まれる区間を手番で渡されて勝てるか?"""
        if l >= r:
            return 0

        reachable = {dp(l, sl) ^ dp(sr, r) for sl, sr in seg if l <= sl and sr <= r}
        g = 0
        while g in reachable:
            g += 1
        return g

    print("Alice" if dp(0, 100) else "Bob")
