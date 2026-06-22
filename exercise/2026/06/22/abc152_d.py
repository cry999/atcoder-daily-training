N = int(input())

# hist[a][b] = 最高位が a で 1 の位が b の数の個数
hist = [[0] * 10 for _ in range(10)]
for n in range(1, N + 1):
    b = n % 10
    a = n
    while a >= 10:
        a //= 10

    if a == 0 or b == 0:
        continue

    hist[a][b] += 1

ans = 0
for n in range(1, N + 1):
    b = n % 10
    a = n
    while a >= 10:
        a //= 10

    if a == 0 or b == 0:
        continue

    ans += hist[b][a]
print(ans)
