N = int(input())
(*A,) = map(int, input().split())

for i in range(1, N):
    print(*A)
    j = i - 1
    v = A[i]
    while j >= 0 and A[j] > v:
        A[j + 1] = A[j]
        j -= 1
    A[j + 1] = v
print(*A)
