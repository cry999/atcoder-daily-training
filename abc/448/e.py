K, M = map(int, input().split())
MOD = 10007
MAX_BIT = 62

rle = []
for _ in range(K):
    c, l = map(int, input().split())
    rle.append((c, l))

rle.reverse()

# 10 の 2^i 乗を前計算する。
ten_digits = []
for i in range(MAX_BIT):
    if i == 0:
        ten_digits.append(10)
    else:
        ten_digits.append(pow(ten_digits[-1], 2, MOD * M))


def pow10(n: int) -> int:
    res = 1
    for i in range(MAX_BIT):
        if n & (1 << i):
            res = res * ten_digits[i]
            res %= MOD * M
    return res


repunit = []
for i in range(MAX_BIT):
    if i == 0:
        repunit.append(1)
    else:
        r = repunit[-1]
        n = r * pow10(pow(2, i - 1)) + r
        n %= MOD * M
        repunit.append(n)


def repunit_mod(n: int) -> int:
    res = 0
    for i in range(MAX_BIT):
        if n & (1 << i):
            res = res * pow10(pow(2, i)) + repunit[i]
            res %= MOD * M
    return res


d = 0
a = 0
for c, l in rle:
    n = c * repunit_mod(l) * pow10(d)
    a += n
    a %= MOD * M
    d += l

print((a // M) % MOD)
