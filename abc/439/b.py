N = int(input())


def f(n: int) -> int:
    ans = 0
    while n:
        ans += (n % 10) ** 2
        n //= 10
    return ans


dup = set()
dup.add(N)
while True:
    N = f(N)
    if N == 1:
        print("Yes")
        break
    if N in dup:
        print("No")
        break
    dup.add(N)
