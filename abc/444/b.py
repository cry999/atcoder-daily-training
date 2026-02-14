N, K = map(int, input().split())


def digit_sum(n: int) -> int:
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s


ans = 0
for i in range(N + 1):
    if digit_sum(i) == K:
        ans += 1
print(ans)
