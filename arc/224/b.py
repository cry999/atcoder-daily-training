from math import isqrt

T = int(input())

for _ in range(T):
    N = int(input())

    x = isqrt(4 * N)
    if x * x < 4 * N:
        x += 1

    print(2 * N - x)
