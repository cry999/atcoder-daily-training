# >>> atcoder-stat >>>
# started_at  = 2026-09-03T15:17:40+09:00
# solved_at   = 2026-09-03T16:07:50+09:00
# duration_ms = 3010589
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, M = map(int, input().split())
# at[i] := 数字 i を含むペアのインデックス
at = [[] for _ in range(M + 1)]
for i in range(N):
    a, b = map(int, input().split())
    at[a].append(i)
    at[b].append(i)

# count[i] := ペア i が含まれる個数
# A, B ともに含まれない -> count[i] = 0
# A, B の一方のみ含まれる -> count[i] = 1
# A, B の両方が含まれる -> count[i] = 2
count = [0] * N
right = 0
covered = 0  # [left, right) に含まれるペアの個数
# ans[i] := 長さ i の区間のうち、全てのペアを含む区間の数
ans = [0] * (M + 2)
for left in range(1, M + 1):
    right = max(right, left)
    while right <= M and covered < N:
        for i in at[right]:
            count[i] += 1
            covered += count[i] == 1  # 新規に含まれるようになったペアを計上
        right += 1

    if covered < N:
        break

    # left を固定した時、[left, right), [left, right+1), ..., [left, M+1) の区間
    # が全てのペアを含む。
    ans[right - left] += 1
    ans[M + 2 - left] -= 1

    for i in at[left]:
        # left を移動する前に現在位置の数字をペアのどちらかにもつペアの個数を減らす
        count[i] -= 1
        covered -= count[i] == 0  # ペア i は現在の [left, right) に含まれない

# ans の累積和をとる
for i in range(M):
    ans[i + 1] += ans[i]

print(*ans[1:-1])
