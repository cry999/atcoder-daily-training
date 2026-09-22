# >>> atcoder-stat >>>
# started_at  = 2026-09-22T02:07:39+09:00
# solved_at   = 2026-09-22T02:32:52+09:00
# duration_ms = 1513761
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left

N, M, K = map(int, input().split())
(*A,) = map(int, input().split())  # N

# 重要な考察
# 1. i が投票数 c で合格するなら、c 以上の得票数を得れば常に合格 -> 単調性
#   hi 側が常に正。
# 2. 得票数が c+1 以上の候補者が M 人未満であればいい
#   逆に、M 人以上の候補者が c+1 以上になるなら達成不可能
# 3. 現段階での上位 M 人に対して検査すれば良い。
# 4. M 人の確認を毎回行うと O(NM log K) になるので M は前計算する。
#   累積和を用いる
# 5. 対象の i が上位 M 人に入る場合に注意

if N == M:
    print(*[0] * N)
    exit()

ordered = sorted(A)
top_m = ordered[N - M :]
assert len(top_m) == M

top_m_1 = ordered[N - M - 1]
print(f"[DEBUG] {top_m=} {top_m_1=}")

prefix = [0] * (M + 1)
for i in range(M):
    prefix[i + 1] = prefix[i] + top_m[i]

S = sum(A)
ans = []
for i in range(N):
    is_top_ranker = top_m[0] <= A[i]

    lo, hi = -1, K + 2
    while hi - lo > 1:
        x = (lo + hi) // 2
        # i は得票数が追加で x あれば合格可能か ?
        # <-> M 人以上の候補者が A[i]+x+1 以上にならないか?
        j = bisect_left(top_m, A[i] + x + 1)
        print(f"[DEBUG] {x+1=} {j=} {top_m=} {prefix=}")

        # c: M 人以上の候補者が x+1 以上になる場合の最小の追加得票数
        c = j * (A[i] + x + 1) - prefix[j]  # x+1 を未獲得の人たちが必要な追加票数
        if is_top_ranker:
            # i が上位 M 人に入る場合は、i の代わりに top_m_1 を計算に入れる
            c -= x + 1
            c += max(0, (A[i] + x + 1) - top_m_1)

        if S + x + c <= K:
            # x より得票しないと合格不可能
            lo = x
        else:
            hi = x

    print(f"[DEBUG] {i=} {A[i]=} {lo=} {hi=}")
    if S + hi > K:
        ans.append(-1)
    else:
        ans.append(hi)

print(*ans)
