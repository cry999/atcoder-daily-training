# >>> atcoder-stat >>>
# started_at  = 2026-09-24T07:47:30+09:00
# solved_at   = 2026-09-24T07:53:33+09:00
# duration_ms = 363711
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, Q = map(int, input().split())
P = [[int(s == "B") for s in input().strip()] for _ in range(N)]
pre = [[0] * (N + 1) for _ in range(N + 1)]
for i in range(N):
    for j in range(N):
        pre[i + 1][j + 1] = pre[i + 1][j] + pre[i][j + 1] - pre[i][j] + P[i][j]


def calc(x: int, y: int):
    """(0, 0) - (x, y) の長方形に含まれる B の数"""
    qx, rx = divmod(x + 1, N)
    qy, ry = divmod(y + 1, N)

    return qx * qy * pre[N][N] + qy * pre[rx][N] + qx * pre[N][ry] + pre[rx][ry]


def query(a: int, b: int, c: int, d: int):
    """(a, b) - (c, d) の長方形に含まれる B の数"""
    res = calc(c, d)
    if a - 1 >= 0:
        res -= calc(a - 1, d)
    if b - 1 >= 0:
        res -= calc(c, b - 1)
    if a - 1 >= 0 and b - 1 >= 0:
        res += calc(a - 1, b - 1)
    return res


for _ in range(Q):
    a, b, c, d = map(int, input().split())
    print(query(a, b, c, d))
