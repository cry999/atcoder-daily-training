N = int(input())


def f(a: int, b: int):
    return a**3 + a**2 * b + a * b**2 + b**3


a, b = 0, 0
while f(a, b) < N:
    a += 1

ans = f(a, b)
while b <= a:
    b += 1
    while f(a, b) > N:
        ans = min(ans, f(a, b))
        a -= 1

print(ans)
