X, Y, Z = map(int, input().split())
if Z == 1:
    if X == Y:
        print('Yes')
    else:
        print('No')
else:
    if X >= Y*Z and (X-Y*Z) % (Z-1) == 0:
        print('Yes')
    else:
        print('No')
