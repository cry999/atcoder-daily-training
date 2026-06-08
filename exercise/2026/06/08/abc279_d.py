from math import ceil
from math import floor

A, B = map(int, input().split())
x = pow(A / (2 * B), 2 / 3) - 1
f = max(floor(x), 0)
c = max(ceil(x), 0)
print(min(B * f + A / pow(f + 1, 1 / 2), B * c + A / pow(c + 1, 1 / 2)))
