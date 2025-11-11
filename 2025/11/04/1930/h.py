MAX_DIGIT = 62
MOD = 998244353


def modpow(base: int, exp: int) -> int:
    n = 1
    while exp > 0:
        if exp & 1:
            n *= base
            n %= MOD
        base *= base
        base %= MOD
        exp >>= 1
    return n


f = [[0] * (MAX_DIGIT+1) for _ in range(MAX_DIGIT+1)]
s = [[0] * (MAX_DIGIT+1) for _ in range(MAX_DIGIT+1)]

# f を計算
f[0][0] = 1
for i in range(MAX_DIGIT):
    f[i+1][0] = f[i][0]
    for j in range(MAX_DIGIT):
        f[i+1][j+1] = (f[i][j+1] + f[i][j]) % MOD

# s を計算
for i in range(MAX_DIGIT):
    for j in range(MAX_DIGIT):
        s[i+1][j+1] = (s[i][j+1] + s[i][j] + modpow(2, i) * f[i][j]) % MOD


T = int(input())
for _ in range(T):
    N, K = map(int, input().split())
    d = []
    i = 0
    while N > 0:
        if N & 1:
            d.append(i)
        i += 1
        N >>= 1
    d.reverse()

    ans = 0
    sum_d = 0
    for i, di in enumerate(d):
        ans += s[di][K-i] + sum_d * f[di][K-i]
        ans %= MOD
        sum_d += modpow(2, di)
        sum_d %= MOD
    if len(d) == K:
        ans = (ans + sum_d) % MOD
    print(ans)
