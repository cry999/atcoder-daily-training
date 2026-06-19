from math import ceil, log

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
while an >= Y:
    na -= 1
    an //= A

# あとは何回 +B すれば Y 以上になるか？
nb = max(0, (Y - an) // B)

if an + B * nb == Y:
    nb -= 1

print(na + nb)
