# >>> atcoder-stat >>>
# started_at  = 2026-09-24T07:08:23+09:00
# solved_at   = 2026-09-24T07:22:00+09:00
# duration_ms = 817935
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left

N, M, K = map(int, input().split())
(*A,) = map(int, input().split())

# 考察
# 1. i が c 票で合格するか? c 票で合格するならそれ以上でも合格する -> 単調性 -> 二分探索
# 2. i が c 票で合格する <-> i が c 票獲得したとき、c+1 票以上の人間が M 人未満である
# 3. c+1 票以上獲得するか考えるのは、現時点での上位 M 人で十分 (なぜなら、それ以外の人間だと余計に票が必要になるから)
# 4. i が上位 M 人に現状入っている場合は 3 に要注意
# 5. 3 を二分探索のたびに計算すると O(NM logK) になるので、事前に累積和をとっておく
#   -> これで O(N logK) で計算できる。

# 合格者の人数が N 人なら、全員追加票なくとも合格する。
if N == M:
    print(*[0] * N)
    exit()

S = sum(A)

ordered = sorted(A)
top_m = ordered[N - M :]  # 上位 M 人の票数
next_top = ordered[N - M - 1]  # 上位 M 人の次の人の票数

pre_top_m = [0] * (M + 1)
for i in range(M):
    pre_top_m[i + 1] = pre_top_m[i] + top_m[i]

ans = [-1] * N
for i in range(N):
    is_top_ranker = A[i] >= top_m[0]

    lo, hi = A[i] - 1, K + 1
    while hi - lo > 1:
        # x: i が最終的に獲得する票数
        x = (lo + hi) // 2
        # j: x+1 票以下の票数しか持っていない人数
        j = bisect_left(top_m, x + 1)

        votes_needed = (x + 1) * j - pre_top_m[j]
        if is_top_ranker:
            votes_needed -= (x + 1) - A[i]
            votes_needed += max(0, (x + 1) - next_top)

        if S + (x - A[i]) + votes_needed <= K:
            # x+1 票以上の人間が M 人以上できる
            lo = x
        else:
            hi = x

    need = hi - A[i]
    if S + need <= K:
        ans[i] = need

print(*ans)
