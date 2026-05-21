L, R, D, U = map(int, input().split())

ans = 0

# y 軸に並行な黒点の線を数える
for x in range(L + (L % 2), R - (R % 2) + 1, 2):
    up_y = min(max(-x, x), U)
    down_y = max(min(-x, x), D)

    ans += max(0, up_y - down_y + 1)
    # print(f"{x=}: {up_y-down_y+1}")

# x 軸に並行な黒点の線を数える
for y in range(D + (D % 2), U - (U % 2) + 1, 2):
    right_x = min(max(-y, y), R)
    left_x = max(min(-y, y), L)

    # print(f"{y=}: {max(right_x-left_x + 1, 0)}")
    ans += max(0, right_x - left_x + 1)

# かぶっている y = x 上と y = -x 上の点を減らす。
for x in range(L + (L % 2), R - (R % 2) + 1, 2):
    if D <= x <= U:
        ans -= 1
    if x != 0 and D <= -x <= U:
        ans -= 1
print(ans)

# ans = 0
# for x in range(L + (L % 2), R - (R % 2) + 1, 2):
#     ans += max(0, min(abs(x) - 1, U) - max(-abs(x) + 1, D) + 1)
#
# for y in range(D + (D % 2), U - (U % 2) + 1, 2):
#     ans += max(0, min(abs(y), R) - max(-abs(y), L) + 1)
#
# print(ans)
