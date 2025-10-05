import math

T = int(input())


def min_dist(
    x0: float, y0: float,
    dx: float, dy: float,
    min_t: int, max_t: int,
) -> float:
    if dx == 0 and dy == 0:
        return math.sqrt(x0*x0 + y0*y0)
    pibot = - (x0*dx + y0*dy) / (dx*dx + dy*dy)
    if pibot < min_t:
        t = min_t
    elif pibot < max_t:
        t = pibot
    else:
        t = max_t
    return math.sqrt((x0+t*dx)**2 + (y0+t*dy)**2)


for _ in range(T):
    TSx, TSy, TGx, TGy = map(int, input().split())
    ASx, ASy, AGx, AGy = map(int, input().split())
    DT = ((TSx - TGx) ** 2 + (TSy - TGy) ** 2) ** 0.5
    DA = ((ASx - AGx) ** 2 + (ASy - AGy) ** 2) ** 0.5

    dxT = (TGx - TSx) / DT
    dyT = (TGy - TSy) / DT
    # print('dxT, dyT:', dxT, dyT)

    dxA = (AGx - ASx) / DA
    dyA = (AGy - ASy) / DA
    # print('dxA, dyA:', dxA, dyA)

    # t 秒後の 2 点の最小距離を求める
    # 1. t < min(DT, DA) の場合 -> 2 次関数 (下に凸)
    ans = min_dist(TSx-ASx, TSy-ASy, dxT-dxA, dyT-dyA, 0, min(DT, DA))

    # 2. min(DT, DA) <= t < max(DT, DA) -> 片方は止まっている
    if DT < DA:  # T がすでに止まっている
        x0, y0 = ASx - TGx, ASy - TGy
        dx, dy = dxA, dyA
    else:  # A がすでに止まっている
        x0, y0 = TSx - AGx, TSy - AGy
        dx, dy = dxT, dyT
    ans = min(ans, min_dist(x0, y0, dx, dy, min(DT, DA), max(DT, DA)))

    print(ans)
