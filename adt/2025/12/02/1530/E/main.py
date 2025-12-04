N = int(input())

MOD = 998244353

# c[i][j] = i 桁目が j である数の個数
c = [[0] * 10 for _ in range(N)]

for j in range(1, 10):
    c[0][j] = 1

for i in range(N-1):
    for j in range(1, 10):
        c[i+1][j] += c[i][j]
        c[i+1][j] %= MOD
        if j-1 >= 1:
            c[i+1][j-1] += c[i][j]
            c[i+1][j-1] %= MOD
        if j+1 <= 9:
            c[i+1][j+1] += c[i][j]
            c[i+1][j+1] %= MOD

print(sum(c[-1]) % MOD)
