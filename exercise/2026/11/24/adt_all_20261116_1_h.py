# >>> atcoder-stat >>>
# started_at  = 2026-11-24T07:59:21+09:00
# solved_at   = 2026-11-24T08:32:43+09:00
# duration_ms = 2002514
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
import sys
from bisect import bisect_right

N, M, K = map(int, input().split())
(*A,) = map(int, input().split())
S = sorted(A, reverse=True)

if N == M:
    print(*[0] * N)
    sys.exit()

top_m = S[:M][::-1]
prefix_m = [0] * (M + 1)
for i in range(M):
    prefix_m[i + 1] = prefix_m[i] + top_m[i]

top_next = S[M]
print(f"[DEBUG] {top_m=} {prefix_m=} {top_next=}")

R = K - sum(A)  # 残りの票数

ans: list[int] = []
for i in range(N):
    lo, hi = -1, R + 2
    while hi - lo > 1:
        # i が追加で x 票獲得したら当選確定するか？
        x = (lo + hi) // 2
        final = A[i] + x  # 最終票数

        # j: i より上位が確定していない候補者の数
        j = bisect_right(top_m, final)
        # need: j 人の候補者が i より票数を稼ぐのに必要な追加の票数
        need = j * (final + 1) - prefix_m[j]

        if A[i] >= top_m[0]:
            # i が top_m に含まれる場合、top_next を上位 M 人に変更する
            need -= max(0, (final + 1) - A[i])
            need += final + 1 - top_next

        print(f"[DEBUG] {i=} {x=}({final=}) {need=}")

        if x + need <= R:
            # この票数では i より票数を稼ぐ候補が M 人以上存在できる
            lo = x
        else:
            hi = x

    print(f"[DEBUG] {lo=} {hi=}")
    if hi > R:
        # R 票以内で当選確定できない場合
        ans.append(-1)
    else:
        ans.append(hi)
print(*ans)
