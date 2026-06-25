N, M = map(int, input().split())
(*A,) = map(int, input().split())

# C[i] := sum(A[:i]) % M
C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = (C[i] + A[i]) % M

hist = {0: 1}
ans = 0
for r in range(1, N + 1):
    hist.setdefault(C[r], 0)
    ans += hist[C[r]]
    hist[C[r]] += 1
print(ans)
