from math import sqrt

N, M = map(int, input().split())

# (x, y, r)
confirmed = [tuple(map(int, input().split())) for _ in range(N)]
# (x, y)
not_confirmed = [tuple(map(int, input().split())) for _ in range(M)]

# O((N+M)M log(200)) だから O(10^4) くらいのオーダーか?


def is_conflict(r0: float):
    """not_confirmed の円の半径を r0 にしたとき交わる円が存在するか?"""
    r0 = mid
    for i, (x0, y0) in enumerate(not_confirmed):
        for x1, y1, r1 in confirmed:
            d = sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
            if abs(r1 - r0) < d < r1 + r0:
                # 交わるのでアウト
                return True
        for x1, y1 in not_confirmed[i + 1 :]:
            d = sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
            if d < 2 * r0:
                return True
    return False


lo, hi = 0, min(r for _, _, r in confirmed or [(0, 0, 201)])
eps = 1e-10
while hi - lo > eps:
    mid = (hi + lo) / 2

    # not_confirmed の半径を mid 以下にできるか?
    # -> 全ての円の半径を mid にして、交わらなければ lo = mid
    # else hi = mid
    # lo 側が true で hi 側が false になる。
    if not is_conflict(mid):
        lo = mid
    else:
        hi = mid

print(lo)
