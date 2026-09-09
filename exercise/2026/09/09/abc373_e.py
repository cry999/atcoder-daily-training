# >>> atcoder-stat >>>
# started_at  = 2026-09-09T08:37:11+09:00
# solved_at   = 2026-09-09T09:07:07+09:00
# duration_ms = 1796493
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left

N, M, K = map(int, input().split())
(*A,) = map(int, input().split())

if N == M:
    print(*[0] * N)
    exit()

# 重要な考察
# 1. 上位 M 人に自分 (注目している i) が入るためにはどんな条件が必要か?
# 2. 自分が k 票追加で獲得して X 票になったとする。X+1 票が M 人以上できるか?
# 3. X+1 票以上になる M 人の候補は自分をのぞいた上位 M 人で良い。
# 4. 「自分をのぞいた」上位 M 人なので、対象が上位 M 人に入るかどうかで分岐がある。

# やること
# 1. 各 i の現在の順位。
# 2. 各 i について、当選するのに必要な最小の票数 (追加ではなく総票数) を二分探索
# 3. (これで計算量は O(N log N) になる)
# 4. M 人を x+1 票以上にするのに必要な票数を毎回数え上げていると O(M) かかるので累積和を利用する。

B = sorted(A)
prefix = [0] * (N + 1)
for i in range(N):
    prefix[i + 1] = prefix[i] + B[i]

R = K - sum(A)  # 残りの票数
ans = [0] * N
for i in range(N):
    rank = N - bisect_left(B, A[i])

    lo, hi = A[i] - 1, A[i] + R + 2
    while hi - lo > 1:
        x = (lo + hi) // 2

        # 自分以外の上位 M 人が x+1 票以上になるのに必要な票数を数える
        other_need = 0
        j = bisect_left(B, x + 1)
        if N - M <= j:
            other_need -= prefix[j] - prefix[N - M]
            other_need += (x + 1) * (j - (N - M))

        if rank <= M:  # 自分が上位 M 人に入っているなら修正
            other_need -= max(0, x + 1 - A[i])
            other_need += max(0, x + 1 - B[N - M - 1])

        my_need = x - A[i]

        if other_need + my_need <= R:
            # 条件を満たしていない(負ける可能性のある票数)
            lo = x
        else:
            hi = x

    if hi <= A[i] + R:  # 実現可能な票数
        ans[i] = hi - A[i]
    else:
        ans[i] = -1

print(*ans)
