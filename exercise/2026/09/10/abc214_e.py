# >>> atcoder-stat >>>
# started_at  = 2026-09-10T10:04:46+09:00
# solved_at   = 2026-09-10T10:26:31+09:00
# duration_ms = 1305310
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

    secs = [tuple(map(int, input().split())) for _ in range(N)]
    secs.sort()

    # 1. i を 1 から 10^9 まで順番にみていく。
    # 2. L == i となる区間について、対応する R を昇順に追加
    # 3. R が積まれていれば 1 つ消化
    # 4. 積まれている R が i より小さければ失敗
    #
    # このまま i を走査すると O(10^9) かかってしまうので、L の値が変化するタイミングだけを走査する。
    # 1. L の昇順にソートする。
    # 2. R が積まれていれば、前回処理した L の一から今回の L の一歩手前まで R を消化する。
    # 3. 同じ L に対して R を全部積む。

    def solve():
        last_l = 0
        stack_r = SortedList()

        i = 0
        while i < N:
            l, _ = secs[i]
            print(f"[DEBUG] === {l=} ===")
            while i < N and secs[i][0] == l:
                print(f"[DEBUG] stack {secs[i]=} [{i=}]")
                _, r = secs[i]
                stack_r.add(r)
                i += 1
            print(f"[DEBUG] {stack_r=}")

            limit = secs[i][0] if i < N else 10**9 + 1
            while stack_r and l <= min(stack_r[0], limit - 1):
                r = stack_r.pop(0)
                print(f"[DEBUG] put {r=} on {l=}")
                l += 1
        return not stack_r

    print("Yes" if solve() else "No")
