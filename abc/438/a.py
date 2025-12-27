D, F = map(int, input().split())

r = D % 7
if r < F:
    print(F-r)
else:
    print(7+F-r)
