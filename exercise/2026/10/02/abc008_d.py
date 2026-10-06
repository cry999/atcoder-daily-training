# >>> atcoder-stat >>>
# started_at  = 2026-10-02T11:02:42+09:00
# solved_at   = 2026-10-02T11:45:24+09:00
# duration_ms = 2562624
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import functools

W, H = map(int, input().split())
N = int(input())
machines = [tuple(map(int, input().split())) for _ in range(N)]


@functools.cache
def dfs(x1: int, x2: int, y1: int, y2: int):
    """(x1, y1) から (x2, y2) までの長方形領域での金塊回収最適解を導き出す"""
    if x1 > x2 or y1 > y2:
        return 0

    res = 0
    for x, y in machines:
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            continue

        # (x, y) の機会を作動させたことによる回収
        score = (x2 - x1 + 1) + (y2 - y1 + 1) - 1
        score += dfs(x1, x - 1, y1, y - 1)  # 左上
        score += dfs(x1, x - 1, y + 1, y2)  # 左下
        score += dfs(x + 1, x2, y1, y - 1)  # 右上
        score += dfs(x + 1, x2, y + 1, y2)  # 右下

        res = max(res, score)

    return res


print(dfs(1, W, 1, H))
