import sys
from functools import cmp_to_key

input = sys.stdin.readline


def half(p: tuple[int, int]) -> int:
    x, y = p
    if y > 0 or (y == 0 and x > 0):
        return 0
    return 1


def cmp(a: tuple[int, int], b: tuple[int, int]) -> int:
    ha, hb = half(a), half(b)
    if ha != hb:
        return ha - hb
    return a[1] * b[0] - a[0] * b[1]


T = int(input())
for _ in range(T):
    N = int(input())

    points: list[tuple[int, int]] = sorted(
        filter(
            lambda p: p[0] != 0 or p[1] != 0,
            [tuple(map(int, input().split())) for _ in range(N)],
        ),
        key=cmp_to_key(cmp),
    )

    n = len(points)
    prefix = [half(p) for p in points]
    prefix += [h + 2 for h in prefix]
    points += points

    ans = 0
    r = 0
    for l in range(n):
        while r < l + n:
            d = prefix[r] - prefix[l]
            if d == 0:
                r += 1
                continue
            if d == 1:
                l1, l2 = points[l]
                r1, r2 = points[r]
                if l1 * r2 - l2 * r1 > 0:
                    r += 1
                    continue
            break

        ans = max(ans, r - l)
    print(ans)
