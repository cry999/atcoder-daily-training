N, X, Y = map(int, input().split())

red = 1
blue = 0

n = N
while n > 1:
    blue = red * X + blue * Y
    red += blue
    n -= 1

print(blue * Y)
