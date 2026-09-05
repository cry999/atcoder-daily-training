# >>> atcoder-stat >>>
# started_at  = 2026-09-05T12:00:50+09:00
# solved_at   = 2026-09-05T12:08:52+09:00
# duration_ms = 482845
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, Q = map(int, input().split())
P = [input() for _ in range(N)]

S = [[0] * (N + 1) for _ in range(N + 1)]
for i in range(N):
    for j in range(N):
        S[i + 1][j + 1] = S[i + 1][j] + S[i][j + 1] - S[i][j] + int(P[i][j] == "B")


def cnt(h: int, w: int):
    """(0, 0) と (h, w) を対角線にもつ長方形に含まれる黒の数"""
    qh, rh = divmod(h, N)
    qw, rw = divmod(w, N)

    return (
        S[N][N] * qh * qw  # 全体が含まれる
        + S[N][rw] * qh  # 横にはみ出ている (縦は全体)
        + S[rh][N] * qw  # 縦にはみ出ている (横は全体)
        + S[rh][rw]  # 縦横にはみ出ている
    )


for _ in range(Q):
    a, b, c, d = map(int, input().split())
    ans = cnt(c + 1, d + 1) - cnt(a, d + 1) - cnt(c + 1, b) + cnt(a, b)
    print(ans)
