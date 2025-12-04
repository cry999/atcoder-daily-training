MOD = 998244353
n = int(input())

ans = n*(n+1) // 2
base = 10
while True:
    # print(n, ans, base)
    if n < base:
        print(ans)
        break
    ans -= (base - base//10)*(n - base + 1)
    ans %= MOD
    base *= 10
