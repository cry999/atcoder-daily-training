N, K = map(int, input().split())

MOD = 10**9 + 7

ans = 0
for k in range(K, N + 2):
    start = k * (k - 1) // 2
    end = k * N - k * (k - 1) // 2

    ans += end - start + 1
    ans %= MOD
print(ans)
