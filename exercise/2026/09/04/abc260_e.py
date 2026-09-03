# >>> atcoder-stat >>>
# started_at  = 2026-09-04T06:15:41+09:00
# solved_at   = 2026-09-04T06:25:55+09:00
# duration_ms = 614366
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


N, M = map(int, input().split())
# at[i] := 数字 i をもつペアの番号リスト
at = [[] for _ in range(M + 1)]
for i in range(N):
    a, b = map(int, input().split())
    at[a].append(i)
    at[b].append(i)

# count[i] := ペア i に含まれる数が現在ターゲットとしている区間に含まれる個数
# count[i] = 0: A[i], B[i] どちらも含まれない
# count[i] = 1: A[i], B[i] のどちらかのみ含まれる
# count[i] = 2: A[i], B[i] ともに含まれる
count = [0] * N
# covered: 現在ターゲットとしている区間に含まれるペアの個数
covered = 0

right = 0
ans = [0] * (M + 2)
for left in range(1, M + 1):
    right = max(right, left)
    while right <= M and covered < N:
        for i in at[right]:
            count[i] += 1
            covered += count[i] == 1  # 初出現のペアをカウントアップ
        right += 1

    if covered < N:
        break

    ans[right - left] += 1
    ans[M + 1 - left + 1] -= 1

    for i in at[left]:
        count[i] -= 1
        covered -= count[i] == 0

for i in range(M + 1):
    ans[i + 1] += ans[i]

print(*ans[1:-1])
