import os
import sys
import bisect

DEBUG = os.environ.get("DEBUG", "0") == "1"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N = int(input())
points = [tuple(map(int, input().split())) for _ in range(N)]
points.sort()


def point_exists(p: tuple[int, int]) -> bool:
    i = bisect.bisect_left(points, p)
    return i < N and points[i] == p


cnt = 0
for i in range(N):
    ld = points[i]
    for j in range(i+1, N):
        ru = points[j]
        if ld[0] == ru[0] or ld[1] >= ru[1]:
            # 左下の点と右上の点の x, y 座標はどちらも
            # 異ならないと長方形にはならない
            continue
        lu = (ld[0], ru[1])
        rd = (ru[0], ld[1])
        if point_exists(lu) and point_exists(rd):
            debug(f'rectangle: {ld}, {ru}')
        cnt += point_exists(lu) and point_exists(rd)

print(cnt)
