N = int(input())
(*A,) = map(int, input().split())
A.sort(reverse=True)

n = A[0]
r = 0
j = 0
for i in range(1, N):
    if n - A[i] < A[i] and r <= n - A[i]:
        r = n - A[i]
        j = i
    elif n - A[i] >= A[i] and r <= A[i]:
        r = A[i]
        j = i
print(n, A[j])
