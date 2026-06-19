from math import isqrt

SCALE = 10**4


def parse(s: str):
    if s[0] == "-":
        return -parse(s[1:])
    if "." in s:
        i = s.index(".")
        a, b = s.ljust(i + 4 + 1, "0").split(".")
    else:
        a, b = s, "0"

    return int(a) * SCALE + int(b)


X, Y, R = map(parse, input().split())
x_int, x_frac = divmod(X, SCALE)
ceil_x = x_int + int(x_frac > 0)
floor_x = x_int


def is_inside(x: int, y: int):
    return (x * SCALE - X) ** 2 + (y * SCALE - Y) ** 2 <= R**2


upper = (Y + R) // SCALE
lower = -((-(Y - R)) // SCALE)
ans = 0
for y in range(lower, upper + 1):
    dy = y * SCALE - Y
    r = R**2 - dy**2
    if r < 0:
        continue

    dx = isqrt(r)

    max_x = (X + dx) // SCALE
    min_x = -((-(X - dx)) // SCALE)

    ans += max_x - min_x + 1
print(ans)
