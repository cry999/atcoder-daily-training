N = int(input())
(*C,) = map(int, input().split())

INF = 10**18
ans = [INF] * N
for i in range(1, N):
    if C[i] != C[i - 1]:
        ans[i] = 1
    else:
        ans[i] = min(ans[i], ans[i - 1] + 1)
for i in range(N - 1, 0, -1):
    if C[i] != C[i - 1]:
        ans[i - 1] = 1
    else:
        ans[i - 1] = min(ans[i - 1], ans[i] + 1)
print(*ans)
