# >>> atcoder-stat >>>
# started_at  = 2026-10-03T12:02:51+09:00
# solved_at   = 2026-10-03T12:09:00+09:00
# duration_ms = 369801
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import functools

W, H = map(int, input().split())
N = int(input())
machines = [tuple(map(int, input().split())) for _ in range(N)]


@functools.cache
def dfs(x1: int, y1: int, x2: int, y2: int):
    if x1 > x2 or y1 > y2:
        return 0

    ans = 0
    for x, y in machines:
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            continue
        score = (x2 - x1 + 1) + (y2 - y1 + 1) - 1
        score += dfs(x1, y + 1, x - 1, y2)  # 左上
        score += dfs(x1, y1, x - 1, y - 1)  # 左下
        score += dfs(x + 1, y + 1, x2, y2)  # 右上
        score += dfs(x + 1, y1, x2, y - 1)  # 右下
        ans = max(ans, score)
    return ans


print(dfs(1, 1, W, H))
