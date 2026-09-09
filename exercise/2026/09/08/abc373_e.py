# >>> atcoder-stat >>>
# started_at  = 2026-09-08T12:40:37+09:00
# solved_at   = 2026-09-08T14:51:34+09:00
# duration_ms = 7857971
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 1
# <<< atcoder-stat <<<
from bisect import bisect_left

N, M, K = map(int, input().split())
(*A,) = map(int, input().split())

if N == M:
    print(*[0] * N)
    exit()


B = sorted(A)
S = sum(A)

prefix = [0] * (N + 1)
for i in range(N):
    prefix[i + 1] = prefix[i] + B[i]

remain = K - sum(A)  # 残りの票

ans = [-1] * N
for i in range(N):
    rank = N - bisect_left(B, A[i])
    # i が当選するために追加で必要な票を二分探索する
    lo, hi = -1, remain + 2
    while hi - lo > 1:
        # mid を追加でもらう場合。
        mid = (lo + hi) // 2
        X = A[i] + mid
        # i を除く上位 M 人が X+1 票以上集めるために必要な票数 C を数える。
        C = 0
        j = bisect_left(B, X + 1)
        # N-M ~ j の人は X+1-B[j] 票追加で必要
        if N - M <= j:
            C -= prefix[j] - prefix[N - M]
            C += (j - (N - M)) * (X + 1)
        if rank <= M:
            C -= max(0, X + 1 - A[i])  # A[i] の影響を除去
            C += max(0, X + 1 - B[N - M - 1])  # A[i] の代わりの上位 M 人目

        if C + mid <= remain:
            lo = mid
        else:
            hi = mid

    if hi <= remain:
        ans[i] = hi
    else:
        ans[i] = -1

print(*ans)
