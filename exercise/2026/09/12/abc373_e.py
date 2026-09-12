# >>> atcoder-stat >>>
# started_at  = 2026-09-12T17:21:59+09:00
# solved_at   = 2026-09-12T17:46:04+09:00
# duration_ms = 1445872
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

if N == M:
    print(*[0] * N)
    exit()

S = sum(A)

# i が当選するには何票必要か?
# -> i が X 票になった時当選するか?
# -> X+1 票になれる人が M 人以上いたらだめ
# -> 現在の上位 M 人の票数を管理する。
# -> 上位 M 人の票数の追加分を毎回計算すると O(NM log N) になるのでだめ
# -> 上位 M 人の票数を累積和で持っておく

(*top_m,) = reversed(sorted(A, reverse=True)[: M + 1])
top_m, top_m_1 = top_m[1:], top_m[0]

prefix_top_m = [0] * (M + 1)
for i in range(M):
    prefix_top_m[i + 1] = prefix_top_m[i] + top_m[i]

print(f"[DEBUG] {top_m=}")

ans = [-1] * N
for i in range(N):
    # i が上位 M にんに入っているかどうか
    is_top_ranker = A[i] >= top_m[0]

    lo, hi = A[i] - 1, 10**18
    while hi - lo > 1:
        # x: i が最終的に確保する票数 (仮定)
        x = (lo + hi) // 2

        # i が x 票になるために必要な票数
        need_i = x - A[i]

        # 上位 m 人が x+1 票以上になるために必要な票数の合計
        j = bisect_left(top_m, x + 1)
        need_m = j * (x + 1) - prefix_top_m[j]
        if is_top_ranker:
            need_m -= max(0, x + 1 - A[i])
            need_m += max(0, x + 1 - top_m_1)

        if S + need_i + need_m <= K:
            # x 票だと上位 M 人に入れない可能性がある
            lo = x
        else:
            hi = x

    if S + hi - A[i] <= K:
        ans[i] = hi - A[i]
print(*ans)
