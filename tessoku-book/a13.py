N, K = map(int, input().split())
A = list(map(int, input().split()))

j = 0
count = 0
for i in range(N):
    j = max(j, i)
    while j < N and A[j] - A[i] <= K:
        j += 1
    j -= 1
    count += j - i

print(count)
