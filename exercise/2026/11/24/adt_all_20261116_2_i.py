# >>> atcoder-stat >>>
# started_at  = 2026-11-24T11:08:29+09:00
# solved_at   = 2026-11-24T11:47:49+09:00
# duration_ms = 2360123
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
from math import gcd

sys.setrecursionlimit(10**7)

N, M, Y = map(int, input().split())
(*A,) = map(int, input().split())

comb = [1] * (N + 1)
for i in range(1, N + 1):
    if i > M:
        comb[i] = comb[i - 1] * i // (i - M)

sig = [0] * (N + 1)
for i in range(M, N + 1):
    sig[i] = 1 if (i - M) % 2 == 0 else -1


def dfs(i: int, n: int, m: int) -> int:
    """すでに n 種類選択して最小公倍数が m である状態から A[i] の取捨を考える"""
    if i == N:
        return 0

    res = 0
    # i を追加する場合
    nxt_m = m * A[i] // gcd(m, A[i])
    if nxt_m <= Y:
        if n + 1 >= M:
            res += sig[n + 1] * comb[n + 1] * (Y // nxt_m)

        res += dfs(i + 1, n + 1, nxt_m)

    # i を追加しない場合
    res += dfs(i + 1, n, m)

    return res


print(dfs(0, 0, 1))
