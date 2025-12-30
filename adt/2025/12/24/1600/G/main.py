import math

A, B = map(int, input().split())

alpha = math.pow(A / 2 / B, 2 / 3) - 1

c = max(0, math.ceil(alpha))
f = max(0, math.floor(alpha))


def func(x: float) -> float:
    global A, B
    return x * B + A / math.sqrt(1 + x)


print(f"{min(func(c), func(f)):.10f}")
