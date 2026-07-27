N = int(input())
(*A,) = map(int, input().split())

MOD = 998244353
inv = [0] * (N + 1)
inv[1] = 1

for a in range(2, N + 1):
    q, r = divmod(MOD, a)
    inv[a] = (-q * inv[r]) % MOD

C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = C[i] + A[i]

ans = 0
s = 0
for i in range(N):
    s += C[N - i] - C[i]
    s %= MOD
    ans += s * inv[i + 1]
    ans %= MOD
print(ans)
