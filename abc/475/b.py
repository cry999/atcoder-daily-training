import math

N = int(input())
(*A,) = map(int, input().split())

coin = [0, 0, 0]  # 1, 10, 100

for a in A:
    n = math.ceil(a / 1000)
    changes = n * 1000 - a
    coin[0] += changes % 10
    changes //= 10
    coin[1] += changes % 10
    changes //= 10
    coin[2] += changes

print(*coin)
