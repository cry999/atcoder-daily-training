def f(x: int) -> int:
    return x * (x + 1) // 2


# N = int(input())
N = 288
decade = 1

ans = 0
for _ in range(15):
    digit = N // decade % 10
    print(digit, decade)
    ans += (N // decade // 10)*f(9)
    decade *= 10

# print(ans)
print(
    (28*f(9) + f(8-1)*1 + 8*(0+1))
    + (2*f(9)*10 + f(8-1)*10 + 8*(8+1))
    + (0*f(9)*100 + f(2-1)*100 + 2*(88+1))
)
