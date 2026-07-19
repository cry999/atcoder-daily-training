T = int(input())


def solve():
    px, py, qx, qy, rx, ry, sx, sy = map(int, input().split())
    dx1, dy1, c1 = px - qx, py - qy, px**2 + py**2 - qx**2 - qy**2
    dx2, dy2, c2 = rx - sx, ry - sy, rx**2 + ry**2 - sx**2 - sy**2
    if dx1 * dx2 < 0:
        dx2, dy2, c2 = -dx2, -dy2, -c2

    if dx1 * dy2 == dx2 * dy1:
        # 平行線の可能性。同一直線なら OK。そうでなければ NG
        if dx1 == 0:  # 条件より dy1 != 0 なので dx2 = 0
            return c1 * dy2 == c2 * dy1
        if dy1 == 0:  # 条件より dx1 != 0 なので dy2 = 0
            return c1 * dx2 == c2 * dx1
        # どっちも 0 ではない。切片が等しいかどうかをみる。
        return c1 * dx2 == c2 * dx1

    # 平行線ではないので必ず接点がある
    return True


for _ in range(T):
    if solve():
        print("Yes")
    else:
        print("No")
