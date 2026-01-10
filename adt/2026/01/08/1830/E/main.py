N = int(input())

MOD = 998244353

d = 1
ans = 0
while N >= d:
    dd = d
    offset = d - 1
    d *= 10
    x = min(d - 1, N)
    diff = (x + 1) * x // 2
    diff -= (dd - 1) * dd // 2
    diff -= offset * (x - dd + 1)
    ans += diff
    ans %= MOD

print(ans)
