def divisors(n: int) -> list[int]:
    d = 1
    ans = []
    stack = []
    while d * d <= n:
        if n % d == 0:
            ans.append(d)
            stack.append(n//d)
        d += 1
    while stack:
        ans.append(stack.pop())
    return ans


for d in divisors(int(input())):
    print(d)
