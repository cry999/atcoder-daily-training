# >>> atcoder-stat >>>
# started_at  = 2026-09-22T17:53:40+09:00
# solved_at   = 2026-09-22T18:14:58+09:00
# duration_ms = 1278134
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, Q = map(int, input().split())
P = [[int(s == "B") for s in input().strip()] for _ in range(N)]

prefix = [[0] * (N + 1) for _ in range(N + 1)]
for i in range(N):
    for j in range(N):
        prefix[i + 1][j + 1] += (
            prefix[i][j + 1] + prefix[i + 1][j] - prefix[i][j] + P[i][j]
        )
print(f"[DEBUG] {prefix=}")


def cnt_black(x: int, y: int):
    """(0, 0) を右上隅, (x, y) を左下隅とする長方形に含まれる黒ますの個数"""
    if x < 0 or y < 0:
        return 0
    qx, rx = divmod(x + 1, N)
    qy, ry = divmod(y + 1, N)
    print(f"[DEBUG] {x=}, {y=}")
    print(f"[DEBUG]     {qx=}, {rx=}, {qy=}, {ry=}")
    res = qx * qy * prefix[N][N]  # 全部含まれる
    res += qy * prefix[rx][N]  # 縦に余る部分
    res += qx * prefix[N][ry]  # 横に余る部分
    res += prefix[rx][ry]  # 右下の余る部分
    return res


def query(a: int, b: int, c: int, d: int):
    """(a, b) を右上隅, (c, d) を左下隅とする長方形に含まれる黒ますの個数"""
    res = cnt_black(c, d)
    res -= cnt_black(a - 1, d)
    res -= cnt_black(c, b - 1)
    res += cnt_black(a - 1, b - 1)
    return res


for _ in range(Q):
    a, b, c, d = map(int, input().split())
    print(query(a, b, c, d))
