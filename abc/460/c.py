N, M = map(int, input().split())
A = sorted(map(int, input().split()), reverse=True)
B = sorted(map(int, input().split()), reverse=True)

i, j = 0, 0
ans = 0
while i < N and j < M:
    if 2 * A[i] >= B[j]:
        ans += 1
        i += 1
        j += 1
    else:
        j += 1
print(ans)
