x, y = map(int, input().split())


def gcd(a: int, b: int):
    if a < b:
        return gcd(b, a)

    if b == 0:
        return a

    return gcd(b, a % b)


print(gcd(x, y))
