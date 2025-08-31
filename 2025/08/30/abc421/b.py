X, Y = map(int, input().split())


def f(a: int) -> int:
    return int(''.join(reversed(str(a))))


a, b = X, Y
for _ in range(8):
    c = f(a + b)
    # print(a, b, c)
    a, b = b, c
print(c)
