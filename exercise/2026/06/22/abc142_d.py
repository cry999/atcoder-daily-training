from math import gcd

A, B = map(int, input().split())
G = gcd(A, B)

ans = 1
for i in range(2, min(G, 10**6) + 1):
    if G == 1:
        break
    if G % i != 0:
        continue

    ans += 1
    while G % i == 0:
        G //= i

if G > 1:
    # G 自身が素数の可能性
    ans += 1
print(ans)
