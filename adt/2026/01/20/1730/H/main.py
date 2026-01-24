from collections import defaultdict
from fractions import Fraction
from itertools import product
from functools import cache

(*A,) = map(int, input().split())

deme = [defaultdict(Fraction) for _ in range(6)]
for n in range(1, 6):
    for idxs in product(range(6), repeat=n):
        # n 個のサイコロがどの面を出目としたかが idxs で表現されている。
        deme[n][tuple(sorted(idxs))] += Fraction(1, 6**n)


@cache
def f(k: int, S: tuple[int, ...]) -> Fraction:
    if len(S) == 5:
        # 全ての出目をキープしている。
        counts = defaultdict(int)
        for i in S:
            counts[A[i]] += 1
        return max(k * v for k, v in counts.items())

    not_keep = 5 - len(S)  # キープしていないダイスの数
    ans = 0
    for idxs in product(range(6), repeat=not_keep):
        # キープしていないダイスの出目を全探索
        prob = Fraction(1, 6**not_keep)
        t_generator = range(1 << not_keep) if k != 1 else [(1 << not_keep) - 1]
        ans += prob * max(
            f(
                k - 1,
                tuple(
                    sorted(
                        S + tuple(idx for i, idx in enumerate(idxs) if (keep >> i) & 1)
                    )
                ),
            )
            for keep in t_generator
        )

    return ans


print(f"{float(f(3, tuple())):.10f}")
