import sys
import numpy as np
from scipy.optimize import linear_sum_assignment

input = sys.stdin.readline

INF = 10**18


def hungarian(cost: list[list[int]]):
    m = np.asarray(cost, dtype=np.int64)
    rows, cols = linear_sum_assignment(m)
    return int(m[rows, cols].sum())


T = int(input())
for _ in range(T):
    N = int(input())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))

    # 偶奇ごとに、絶対値を昇順に並べる
    aa = [sorted(abs(x) for x in A if x % 2 == parity) for parity in range(2)]
    bb = [sorted(abs(x) for x in B if x % 2 == parity) for parity in range(2)]

    # op[p]：加算回数の偶奇がpの場合の最小実現可能回数
    op = [INF, INF]

    for parity in range(2):
        if any(len(aa[q]) != len(bb[q ^ parity]) for q in range(2)):
            continue

        required = 0

        for q in range(2):
            for x, y in zip(aa[q], bb[q ^ parity]):
                required = max(required, abs(x - y))

        op[parity] = required

    min_op = min(op)

    if min_op == INF:
        print(-1)
        continue

    # t_min回の加算＋各要素高々2回の反転で達成可能
    ans = min_op + 2 * N

    for t in range(min_op, min_op + 2 * N):
        # 加算だけで現在の答え以上になる
        if t >= ans:
            break

        if t < op[t & 1]:
            continue

        cost = []

        for a in A:
            row = []

            for b in B:
                if (a + b - t) % 2 != 0:
                    c = INF
                elif b == a + t:
                    c = 0
                elif abs(a + b) <= t:
                    c = 1
                elif abs(a - b) <= t:
                    c = 2
                else:
                    c = INF

                row.append(c)

            cost.append(row)

        flips = hungarian(cost)
        ans = min(ans, t + flips)

    print(ans)
