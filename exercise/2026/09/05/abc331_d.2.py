# >>> atcoder-stat >>>
# started_at  = 2026-09-05T04:38:42+09:00
# solved_at   = 2026-09-05T05:07:22+09:00
# duration_ms = 1720035
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 3
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, Q = map(int, input().split())
P = [list(input()) for _ in range(N)]

S = [[0] * (N + 1) for _ in range(N + 1)]
for i in range(N):
    for j in range(N):
        S[i + 1][j + 1] = S[i][j + 1] + S[i + 1][j] - S[i][j] + (P[i][j] == "B")


def __count(h: int, w: int):
    """原点から (h, w) までの長方形に含まれる B の数を返す"""
    qh, rh = divmod(h, N)
    qw, rw = divmod(w, N)

    return (
        S[rh][rw]  # 縦・横ともにはみ出ている部分
        + S[N][rw] * qh  # 縦方向にはみ出ている部分
        + S[rh][N] * qw  # 横方向にはみ出ている部分
        + S[N][N] * qh * qw  # 丸っと含まれる部分
    )


def count(a: int, b: int, c: int, d: int):
    """(a, b) から (c, d) までの長方形に含まれる B の数を返す"""
    a, c = min(a, c), max(a, c)
    b, d = min(b, d), max(b, d)
    return __count(c + 1, d + 1) - __count(a, d + 1) - __count(c + 1, b) + __count(a, b)


for _ in range(Q):
    a, b, c, d = map(int, input().split())

    print(count(a, b, c, d))
