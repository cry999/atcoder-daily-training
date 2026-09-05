# >>> atcoder-stat >>>
# started_at  = 2026-09-05T11:33:34+09:00
# solved_at   = 2026-09-05T11:51:54+09:00
# duration_ms = 1100819
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


# 1. ある部分列が条件を満たすなら、それの左右を伸ばしたものも条件を満たす。
# 2. ある l に対応した条件を満たす最小の r をとると、l+1 に対しては r 以上が条件を満たす。
# 3. 条件を満たすかは、各ペアの要素が幾つ含まれるかと、その個数が 0 と 1 を行き来する時に注目すれば良い

N, M = map(int, input().split())

# at[i] := 数字 i を含むペアのリスト
at = [[] for _ in range(M + 1)]
for i in range(N):
    a, b = map(int, input().split())
    at[a].append(i)
    at[b].append(i)


# count[i] := 現在ターゲットとしている区間にペア i の要素が幾つ含まれているか
count = [0] * (N + 1)
# covered := 現在ターゲットとしている区間に含まれるペアの数
covered = 0

ans = [0] * (M + 2)

right = 0
for left in range(1, M + 1):
    right = max(right, left)
    while right <= M and covered < N:
        for i in at[right]:
            count[i] += 1
            covered += count[i] == 1
        right += 1

    if covered != N:
        # 今全てのペアを含む区間が存在しないなら、left を縮めても存在しないので終了
        break

    # left に対する右端は、right から M+1 まで取れる。
    # したがって、その区間の長さは、right-left ~ M+1-left まで。
    # これの累積和をとる。
    ans[right - left] += 1
    ans[M + 2 - left] -= 1

    print(f"[DEBUG] {left=}, {right=}: [{right-left}]+1 / [{M+2-left}]-1")

    for i in at[left]:
        count[i] -= 1
        covered -= count[i] == 0

print(f"[DEBUG] {ans=}")
for i in range(M + 1):
    ans[i + 1] += ans[i]
print(*ans[1:-1])
