N = int(input())

digits = []
while N:
    digits.append(N % 10)
    N //= 10

digits.sort(reverse=True)

ans = 0
for bit in range(1 << len(digits) - 1):
    if bit == 0:
        continue
    a, b = 0, 0
    for i, d in enumerate(digits):
        if bit & (1 << i):
            a = a * 10 + d
        else:
            b = b * 10 + d
    ans = max(ans, a * b)
print(ans)
