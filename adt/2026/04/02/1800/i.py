import math
import sys

sys.setrecursionlimit(10**7)

N = int(input())


def is_palindrome(s: str) -> bool:
    for i in range(len(s) // 2):
        if s[i] != s[len(s) - i - 1]:
            return False
    return True


def rev(n: int) -> int:
    r = 0
    while n:
        r *= 10
        r += n % 10
        n //= 10
    return r


def f(n: int):
    if n == 0:
        return ""

    s = str(n)
    if is_palindrome(s) and "0" not in s:
        return s

    for x in range(2, math.isqrt(n) + 1):
        if n % x != 0:
            continue

        if "0" in str(x):
            continue

        z = n // x
        y = rev(x)
        if z % y != 0:
            continue

        w = z // y
        t = f(w)
        if t == "":
            continue

        return f"{x}*{t}*{y}"

    return ""


ans = f(N)
if ans == "":
    print(-1)
else:
    print(ans)
