N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

A.sort()
B.sort()

ans = abs(A[0] - B[0])
i, j = 0, 0
while i < N and j < M:
    ans = min(ans, abs(A[i] - B[j]))
    while j + 1 < M and abs(A[i] - B[j]) >= abs(A[i] - B[j + 1]):
        j += 1
        ans = min(ans, abs(A[i] - B[j]))

    i += 1

print(ans)
