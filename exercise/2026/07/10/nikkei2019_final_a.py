N = int(input())
(*A,) = map(int, input().split())
C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = C[i] + A[i]


for k in range(1, N + 1):
    ans = max(C[i + k] - C[i] for i in range(N - k + 1))
    print(ans)
