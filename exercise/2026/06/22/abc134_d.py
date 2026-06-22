N = int(input())
(*A,) = map(int, input().split())

ans = [0] * (N + 1)
for n in range(N, 0, -1):
    cnt = 0
    for m in range(n, N + 1, n):
        cnt ^= ans[m]
    # print(f"{n=}, {cnt=}")
    if cnt != A[n - 1]:
        ans[n] = 1

print(sum(ans))
print(*[i for i in range(N + 1) if ans[i] == 1])
