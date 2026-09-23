# >>> atcoder-stat >>>
# started_at  = 2026-09-24T07:30:30+09:00
# solved_at   = 2026-09-24T07:47:17+09:00
# duration_ms = 1007579
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from collections import defaultdict

N = int(input())
(*A,) = [list(map(int, input().split())) for _ in range(N)]

# 考察
# 1. 全経路は 40C20 = 137,846,528,820 通りで無理
# 2. 対角線までを考えると、sum(20Ci for i in range(21)) = 2^20 = 10^6
# 3. スタートから対角線までの XOR とゴールから対角線までの XOR を計算して、A[i][N-1-i] になるものを列挙すれば良い

from_start = [[defaultdict(int) for _ in range(N)] for _ in range(N)]
from_start[0][0][A[0][0]] = 1
for i in range(N):
    for j in range(N):
        if i + j == N - 1:
            break
        for v, cnt in from_start[i][j].items():
            from_start[i + 1][j][v ^ A[i + 1][j]] += cnt
            from_start[i][j + 1][v ^ A[i][j + 1]] += cnt
print(f"[DEBUG] {from_start=}")
from_goal = [[defaultdict(int) for _ in range(N)] for _ in range(N)]
from_goal[-1][-1][A[-1][-1]] = 1
for i in range(N - 1, -1, -1):
    for j in range(N - 1, -1, -1):
        if i + j == N - 1:
            break
        for v, cnt in from_goal[i][j].items():
            from_goal[i - 1][j][v ^ A[i - 1][j]] += cnt
            from_goal[i][j - 1][v ^ A[i][j - 1]] += cnt
print(f"[DEBUG] {from_goal=}")
ans = 0
for i in range(N):
    j = N - 1 - i
    for v, cnt in from_start[i][j].items():
        ans += from_goal[i][j][v ^ A[i][j]] * cnt
print(ans)
