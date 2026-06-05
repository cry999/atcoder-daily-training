MOD = 998244353

N = int(input())

n = N
pow10 = 1
while pow10 <= N:
    pow10 *= 10

ans = 0
while N:
    if N & 1:
        ans *= pow10
        ans += n
        ans %= MOD

    n = (n * pow10 + n) % MOD
    pow10 *= pow10
    pow10 %= MOD
    N >>= 1

print(ans)
