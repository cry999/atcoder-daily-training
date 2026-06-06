N, M, P = map(int, input().split())
(*A,) = sorted(map(int, input().split()))
(*B,) = sorted(map(int, input().split()), reverse=True)
C = [0] * (M + 1)
for i in range(M):
    C[i + 1] = C[i] + B[i]

ans = 0
j = 0
for i in range(N):
    while j < M and A[i] + B[j] >= P:
        j += 1

    ans += P * j + C[M] - C[j] + A[i] * (M - j)

print(ans)
