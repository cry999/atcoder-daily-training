MOD = 998244353

N = int(input())
(*A,) = map(int, input().split())

# s: A の累積和 / d: A[i] の桁数
s = [0] * (N + 1)
d = [1] * N
for i in range(N):
    s[i + 1] = (s[i] + A[i]) % MOD
    n = A[i]
    while n:
        n //= 10
        d[i] *= 10

ans = 0
for j in range(1, N):
    # print(f"{j=}: {s[j] * d[j] + j * A[j]}")
    ans += s[j] * d[j] + j * A[j]
    ans %= MOD
print(ans)
