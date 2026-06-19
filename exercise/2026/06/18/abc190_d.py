N = int(input())

ans = 0
M = 2 * N
for i in range(1, M + 1):
    if i * i > M:
        break
    if M % i != 0:
        continue

    d1 = i
    d2 = M // i

    if d1 % 2 == d2 % 2:
        # n = (d1 + d2 - 1) // 2 なので、d1 + d2 は奇数でないといけない
        continue

    ans += 2

print(ans)
