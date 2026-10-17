from functools import cmp_to_key
from math import gcd
from fractions import Fraction

# 考察
# 1. (A[i] + C[i]) / (B[i] + D[i]) = (A[j] + C[j]) / (B[j] + D[j]) なので
# (A[i], B[i]) を全て同じ直線上に移動するのが目的?
# 2. なんか C か D はオール 0 でいけるのでは? (知らんけど)


def cmp(p: tuple[int, int], q: tuple[int, int]):
    diff = p[0] * q[1] - p[1] * q[0]
    return (diff > 0) - (diff < 0)


def best_slope(a: list[int], b: list[int]) -> Fraction:
    """-1 <= t <= 1 の範囲で sum(|b[i] - t * a[i]|) を最小化する。"""

    # (値 b[i] / a[i], 重み |a[i]|)
    points = []
    for x, y in zip(a, b):
        if x == 0:
            continue

        d = gcd(x, y) or 1
        if x < 0:
            d = -d
        points.append((y // d, x // d, abs(x)))

    # すべての a[i] が 0 なら、コストは t によらない。
    if not points:
        return Fraction(0)

    points.sort(key=cmp_to_key(cmp))

    sum_w = sum(w for _, _, w in points)

    # 中央値で最小化される。
    c = 0
    for y, x, w in points:
        c += w
        if 2 * c >= sum_w:
            mid = Fraction(y, x or 1)
            break

    # t の範囲を [-1, 1] に制限する。
    return max(Fraction(-1), min(Fraction(1), mid))


N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())


t = best_slope(A, B)
cost1 = 0
for a, b in zip(A, B):
    cost1 += abs(t.denominator * b - t.numerator * a)
cost1 = Fraction(cost1, t.denominator)

s = best_slope(B, A)
cost2 = 0
for a, b in zip(A, B):
    cost2 += abs(s.denominator * a - s.numerator * b)
cost2 = Fraction(cost2, s.denominator)

ans = min(cost1, cost2)
print(ans.numerator, ans.denominator if ans.numerator else 1)
