from bisect import bisect_left

MOD = 998244353

N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

if N > M:
    A, B = B, A
    N, M = M, N

B.sort()
C = [0] * (M + 1)
for i, b in enumerate(B):
    C[i + 1] = C[i] + b
    C[i + 1] %= MOD

ans = 0
for a in A:
    i = bisect_left(B, a)
    ans += 2 * i * a
    ans %= MOD
    ans -= M * a
    ans %= MOD
    ans += C[M]
    ans %= MOD
    ans -= 2 * C[i]
    ans %= MOD

print(ans)
