N, K = map(int, input().split())
(*A,) = map(int, input().split())

if A[-1] < K:
    A.append(K - 1)
else:
    A.append(K + 1)

ans = 0
for i in range(N):
    if A[i] == K or A[i] < K < A[i + 1] or A[i + 1] < K < A[i]:
        ans += 1

print(ans)
