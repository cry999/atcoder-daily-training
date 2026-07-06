m = int(input())
constellation = [tuple(map(int, input().split())) for _ in range(m)]
x0, y0 = constellation[0]

n = int(input())
stars = set(tuple(map(int, input().split())) for _ in range(n))

for x1, y1 in stars:
    # (x0, y0) を (x1, y1) に重ね合わせて星座になるかを確認する
    dx, dy = x1 - x0, y1 - y0

    for x, y in constellation:
        xx, yy = x + dx, y + dy
        if (xx, yy) not in stars:
            break
    else:
        print(dx, dy)
