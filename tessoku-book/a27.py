def gcd(a: int, b: int) -> int:
    if a < b:
        a, b = b, a
    if b == 0:
        return a
    return gcd(b, a % b)


print(gcd(*map(int, input().split())))
