N, M = map(int, input().split())
(*A,) = map(int, input().split())  # N
(*B,) = map(int, input().split())  # N-1

# A[0] に 1 を足さない場合
ans1 = 0
A1 = A.copy()
for i in range(N - 1):
    if (A1[i + 1] + A1[i]) % M != B[i] % M:
        A1[i + 1] = (A1[i + 1] + 1) % M
        ans1 += 1

# A[0] に 1 を足す場合
ans2 = 1
A1 = A.copy()
A1[0] = (A1[0] + 1) % M
for i in range(N - 1):
    if (A1[i + 1] + A1[i]) % M != B[i] % M:
        A1[i + 1] = (A1[i + 1] + 1) % M
        ans2 += 1

ans = min(ans1, ans2)
print(ans)
