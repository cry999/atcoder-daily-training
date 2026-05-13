T = int(input())

for _ in range(T):
    N, X, K = map(int, input().split())

    x = X
    p = float("inf")
    k = K
    ans = 0
    while x and k >= 0:
        if k <= 60:
            d = 1 << k
            ans += min(N + 1, (x + 1) * d) - min(N + 1, x * d)
            if k > 0:
                ans -= min(N + 1, (p + 1) * d // 2) - min(N + 1, p * d // 2)

        x, p, k = x // 2, x, k - 1

    print(ans)
