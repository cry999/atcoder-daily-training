import bisect

MOD = 998244353


N, M = map(int, input().split())
*A, = sorted(map(int, input().split()))
*B, = sorted(map(int, input().split()))

cum_b = [0]*(M+1)

for i in range(M):
    cum_b[i+1] = (cum_b[i] + B[i]) % MOD

ans = 0
for i in range(N):
    j = bisect.bisect_left(B, A[i])
    ans += (2*j - M)*A[i] + (cum_b[M] - 2*cum_b[j] + MOD) % MOD
    ans %= MOD
print(ans)
