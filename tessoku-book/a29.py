MOD = 10**9 + 7
a, b = map(int, input().split())

# mod pow
p = 1
while b:
    if b & 1:
        p = (p * a) % MOD
    a = (a * a) % MOD
    b >>= 1
print(p)
