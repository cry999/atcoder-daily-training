MOD = 10**9 + 7
H, W = map(int, input().split())

a, b = 1, 1
for i in range(1, H+W-1):
    if i < W:
        b = (b * i) % MOD
    if i < H:
        b = (b * i) % MOD
    a = (a * i) % MOD


def mod_pow(a: int, b: int, m: int) -> int:
    p = 1
    while b:
        if b & 1:
            p = (p * a) % m
        a = (a * a) % m
        b >>= 1
    return p


print((a * mod_pow(b, MOD - 2, MOD)) % MOD)
