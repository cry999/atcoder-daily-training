N = int(input())
(*A,) = map(lambda x: int(x) - 1, input().split())

for i in range(N - 1, -1, -1):
    if A[i] == i:
        A[i] = i + 1
    else:
        A[i] = A[A[i]]
print(*A)
