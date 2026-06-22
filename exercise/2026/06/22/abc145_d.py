MOD = 10**9 + 7
X, Y = map(int, input().split())

if (X + Y) % 3 != 0:
    print(0)
    exit()

n = (X + Y) // 3
k = min(X - n, Y - n)
if k < 0:
    print(0)
    exit()

inv = [1] * (n + 1)
for i in range(2, n + 1):
    q, r = divmod(MOD, i)
    inv[i] = (-q * inv[r]) % MOD

c = 1
for i in range(k):
    c = (c * (n - i) * inv[i + 1]) % MOD

print(c)
