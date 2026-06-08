from math import gcd

T = int(input())

for _ in range(T):
    N, D, K = map(int, input().split())
    D %= N
    g = gcd(N, D)
    if g == 1:
        print(((K - 1) * D) % N)
    else:
        q, r = divmod(K - 1, N // g)
        print((q + r * D) % N)
