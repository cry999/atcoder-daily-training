from math import atan2, tan, pi

a, b, x = map(int, input().split())
theta0 = atan2(2 * x, a * a * a)
if b >= a * tan(theta0):
    print(atan2(a * b * b, 2 * x) * 180 / pi)
else:
    print(atan2(2 * (a * a * b - x), a * a * a) * 180 / pi)
