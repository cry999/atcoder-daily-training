from math import sin
from math import cos, pi

N = int(input())

x0, y0 = map(int, input().split())
xh, yh = map(int, input().split())

xc, yc = (xh + x0) / 2, (yh + y0) / 2

c = cos(pi / (N // 2) * (N // 2 - 1))
s = sin(pi / (N // 2) * (N // 2 - 1))

x1 = (xh - xc) * c + (yh - yc) * s + xc
y1 = (yh - yc) * c - (xh - xc) * s + yc

print(x1, y1)
