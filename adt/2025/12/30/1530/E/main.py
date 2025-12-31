import math

N = int(input())


def is_palindrome(s: str) -> bool:
    n = len(s)
    for i in range(n // 2):
        if s[i] != s[n - 1 - i]:
            return False
    return True


for i in range(math.ceil(math.pow(N, 1 / 3)) + 1, 0, -1):
    if i**3 > N:
        continue

    if is_palindrome(str(i**3)):
        print(i**3)
        exit()
