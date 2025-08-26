X, Y = map(int, input().split())

a = (X + Y) % 12
if a == 0:
    print(12)
else:
    print(a)
