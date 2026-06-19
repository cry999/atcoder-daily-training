(*X,) = map(int, list(input()))
M = int(input())

d = 0
for x in X:
    d = max(d, x)

lo, hi = d, 1 << 63
while hi - lo > 1:
    mid = (lo + hi) // 2
    a = 0
    for x in X:
        a = a * mid + x
        if a > M:
            break
    else:
        lo = mid
        continue
    hi = mid

if len(X) == 1:
    if X[0] > M:
        print(0)
    else:
        print(1)
else:
    print(lo - d)
