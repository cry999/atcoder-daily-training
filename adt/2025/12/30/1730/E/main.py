N = int(input())
(*A,) = map(int, input().split())

S = [0] * (N + 1)
for i in range(N):
    S[i + 1] = S[i] + A[i]

ans = 0
for i in range(N):
    ans += A[i] * (S[N] - S[i + 1])
print(ans)
