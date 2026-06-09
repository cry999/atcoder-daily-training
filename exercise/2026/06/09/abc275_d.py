import functools
import sys

sys.setrecursionlimit(10**7)


@functools.cache
def f(k: int):
    if k == 0:
        return 1
    return f(k // 2) + f(k // 3)


print(f(int(input())))
