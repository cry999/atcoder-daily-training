sx, sy = map(int, input().split())
tx, ty = map(int, input().split())

cx, cy = sx, sy
sigx = (tx - sx) // abs(sx - tx) if sx != tx else 0
sigy = (ty - sy) // abs(sy - ty) if sy != ty else 0

d = min(abs(sx - tx), abs(sy - ty))
dx, dy = d * sigx, d * sigy
ans = d
# print(ans)

cx += dx
cy += dy
# print(cx, cy)
if cx == tx and cy == ty:
    # goal
    pass
elif cx == tx:
    # 上下の移動追加
    ans += abs(cy - ty)
else:  # cy == ty
    # 左右の移動追加
    if ty % 2 == 0:
        cx -= cx % 2
        tx -= tx % 2
    else:
        cx += cx % 2
        tx += tx % 2

    ans += abs(cx - tx) // 2

print(ans)
