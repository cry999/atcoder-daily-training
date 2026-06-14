N, K = map(int, input().split())
(*A,) = map(int, input().split())

C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = C[i] + A[i]

hist = {0: 1}

ans = 0
for r in range(1, N + 1):
    # print(f"[DEBUG] {r=}, {C[r]=}, {ans=}, {hist=}")
    ans += hist.get(C[r] - K, 0)
    hist[C[r]] = hist.get(C[r], 0) + 1
print(ans)
