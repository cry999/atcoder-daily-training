N = int(input())

lo, hi = 0, N
while hi - lo > 1:
    mi = (lo + hi) // 2
    print("?", mi + 1)

    c = input()
    if c == "0":
        lo = mi
    else:
        hi = mi

print("!", lo + 1)
