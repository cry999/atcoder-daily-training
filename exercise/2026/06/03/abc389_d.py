R = int(input())

y = R

a = 0  # 軸上に無い
b = 0  # 軸上にある
c = 0  # 原点
for x in range(R):
    while (2 * x + 1) ** 2 + (2 * y + 1) ** 2 > 4 * R**2:
        y -= 1
    # print(x, y)
    if x == 0:
        b += y
        c += 1
    else:
        a += y
        b += 1

print(4 * a + 2 * b + c)
