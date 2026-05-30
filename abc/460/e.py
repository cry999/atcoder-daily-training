from math import gcd

MOD = 998244353

T = int(input())

pow10 = [1] * 20
for i in range(1, 20):
    pow10[i] = pow10[i - 1] * 10

for _ in range(T):
    N, M = map(int, input().split())
    max_d = len(str(N))

    ans = 0
    for i in range(1, max_d + 1):
        a = M // gcd(pow10[i] - 1, M)
        q = N // a
        ans += q * (min(pow10[i], N + 1) - pow10[i - 1]) % MOD
        ans %= MOD

    print(ans)

    # ans = 0
    # for i in range(1, max_d + 1):
    #     for a in range(1, N + 1):
    #         if a % M != (a * pow10[i]) % M:
    #             continue
    #         ans += (min(pow10[i], N + 1) - pow10[i - 1]) % MOD
    #         ans %= MOD
    # print(ans)
    # print("---")
