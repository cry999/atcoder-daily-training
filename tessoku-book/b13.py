N, K = map(int, input().split())
A = list(map(int, input().split()))

C = [0] * (N+1)
for i in range(N):
    C[i+1] = C[i] + A[i]

j, count = 0, 0
for i in range(1, N+1):
    while j < N+1 and C[j] - C[i-1] <= K:
        j += 1
    j -= 1
    count += j - (i - 1)

print(count)
