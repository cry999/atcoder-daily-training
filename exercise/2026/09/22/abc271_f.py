# >>> atcoder-stat >>>
# started_at  = 2026-09-22T17:31:14+09:00
# solved_at   = 2026-09-22T17:49:01+09:00
# duration_ms = 1067862
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from collections import defaultdict

N = int(input())
A = [list(map(int, input().split())) for _ in range(N)]

# 考察
# 1. 全経路は 2N_C_N 通りある。N=20 でも 137,846,528,820 通りなので、全探索は可能。
# 2. 対角線までを考える。スタートから対角線までの全経路は sum(20_C_x for x in range(21)) = 1,048,576 (= 2^20) 通り
# 3. 対角線からゴールまでも同様。
# 4. スタートとゴールから対角線までの経路を全探索して、最後に対角線で 0 になる組み合わせを確かめれば良いので
#   計算量は O(2^N + 2^N + N^2) = O(2^N) で十分間に合う。

# スタートから対角線までの全経路を探索
from_start = [[defaultdict(int) for _ in range(N)] for _ in range(N)]
from_start[0][0][A[0][0]] = 1
for i in range(N):
    for j in range(N):
        if i + j >= N - 1:
            break
        for v, cnt in from_start[i][j].items():
            from_start[i + 1][j][v ^ A[i + 1][j]] += cnt
            from_start[i][j + 1][v ^ A[i][j + 1]] += cnt

from_goal = [[defaultdict(int) for _ in range(N)] for _ in range(N)]
from_goal[N - 1][N - 1][A[N - 1][N - 1]] = 1
for i in range(N - 1, -1, -1):
    for j in range(N - 1, -1, -1):
        if i + j < N:
            break
        for v, cnt in from_goal[i][j].items():
            from_goal[i - 1][j][v ^ A[i - 1][j]] += cnt
            from_goal[i][j - 1][v ^ A[i][j - 1]] += cnt

print(f"[DEBUG] {from_start=}")
print(f"[DEBUG] {from_goal=}")

ans = 0
for i in range(N):
    for v, cnt in from_start[i][N - 1 - i].items():
        print(f"[DEBUG] {i=}, {v=}, {cnt=}, {from_goal[i][N - 1 - i]=}")
        ans += cnt * from_goal[i][N - 1 - i][v ^ A[i][N - 1 - i]]
print(ans)
