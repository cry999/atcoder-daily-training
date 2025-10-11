def f(n: int) -> int:
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s


a = 1
for i in range(int(input())-1):
    # print(i, a)
    a = f(a) + a
print(a)
