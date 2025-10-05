def f(i: int) -> int:
    if i % 2 == 0:
        return i**3
    return -i**3


N = int(input())
print(sum(f(i) for i in range(1, N + 1)))
