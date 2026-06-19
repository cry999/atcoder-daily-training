from math import ceil
from math import log

X, Y, A, B = map(int, input().split())

# xA する回数を数える。
lo, hi = 0, ceil(log(Y / X) / log(A)) + 1
while hi - lo > 1:
    mi = (lo + hi) // 2
    # mi 回目に初めて +B をするのが良いか？
    a = pow(A, mi - 1)
    if a * X * A <= a * X + B:
        lo = mi
    else:
        hi = mi

# lo 回目までは xA するのが良い。
na = lo
an = pow(A, na) * X
# あとは何回 +B すれば Y 以上になるか？
nb = max(0, ceil((Y - an) // B))

print(na + nb)
