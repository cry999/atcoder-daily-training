# >>> atcoder-stat >>>
# started_at  = 2026-09-08T15:49:55+09:00
# solved_at   = 2026-09-08T15:58:27+09:00
# duration_ms = 512412
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList
import sys

input = sys.stdin.readline


N, M = map(int, input().split())
queue = SortedList(range(N))
eaten = [0] * N

waiting = SortedList()
for _ in range(M):
    t, w, s = map(int, input().split())

    # まずは待機列から戻れる人を戻す
    while waiting and waiting[0][0] <= t:
        _, idx = waiting.pop(0)
        queue.add(idx)

    if queue:
        # 先頭の人が食べる
        idx = queue.pop(0)
        print(f"[DEBUG] {t=} {w} eaten by {idx=}")
        eaten[idx] += w
        waiting.add((t + s, idx))

for i in range(N):
    print(eaten[i])
