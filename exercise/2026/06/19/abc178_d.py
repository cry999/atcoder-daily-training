MOD = 10**9 + 7

N = int(input())

f = [0] * (max(N, 3) + 1)
f[3] = 1
for i in range(4, N + 1):
    f[i] = (f[i - 1] + f[i - 3]) % MOD
print(f[N])
