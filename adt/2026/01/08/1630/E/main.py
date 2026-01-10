N, K = map(int, input().split())
(*A,) = map(int, input().split())
B = sorted(A)

ans = B[N - K - 1] - B[0]
for k in range(K + 1):
    l, r = k, N - K + k - 1
    ans = min(ans, B[r] - B[l])
print(ans)
