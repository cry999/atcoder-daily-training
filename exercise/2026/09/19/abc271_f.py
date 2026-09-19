# >>> atcoder-stat >>>
# started_at  = 2026-09-19T11:07:24+09:00
# solved_at   = 2026-09-19T11:44:25+09:00
# duration_ms = 2221737
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
from collections import defaultdict

N = int(input())
A = [list(map(int, input().split())) for _ in range(N)]

B = [[defaultdict(int) for _ in range(N)] for _ in range(N)]
B[0][0][A[0][0]] += 1

for p in range(N * N):
    i, j = divmod(p, N)
    # 左上から初めて、対角線上までを全列挙
    if i + j >= N - 1:
        continue

    for x, cnt in B[i][j].items():
        if i + 1 < N:
            y = x ^ A[i + 1][j]
            B[i + 1][j][y] += cnt
        if j + 1 < N:
            y = x ^ A[i][j + 1]
            B[i][j + 1][y] += cnt


# 右下から始めて、対角線上までを全列挙
C = [[defaultdict(int) for _ in range(N)] for _ in range(N)]
C[N - 1][N - 1][A[N - 1][N - 1]] += 1

for p in range(N * N - 1, -1, -1):
    i, j = divmod(p, N)
    if i + j <= N - 1:
        continue

    for x, cnt in C[i][j].items():
        if i - 1 >= 0:
            y = x ^ A[i - 1][j]
            C[i - 1][j][y] += cnt
        if j - 1 >= 0:
            y = x ^ A[i][j - 1]
            C[i][j - 1][y] += cnt

print(f"[DEBUG] {B=}")
print(f"[DEBUG] {C=}")
ans = 0
for i in range(N):
    j = N - 1 - i
    for x, cnt in B[i][j].items():
        print(f"[DEBUG] {i=} {x=} {cnt=}")
        ans += cnt * C[i][j][x ^ A[i][j]]
print(ans)
