N = int(input())
(*A,) = map(int, input().split())

i = 0
ans = N
while i + 1 < N:
    j = i + 1
    d = A[j] - A[i]
    while j + 1 < N and A[j + 1] - A[j] == d:
        j += 1

    ans += (j - i + 1) * (j - i) // 2
    i = j

print(ans)
