N = int(input())

cnt = 0
for a in range(1, N + 1):
    if a**3 > N:
        break

    for b in range(a, N + 1):
        if a * b**2 > N:
            break

        c = N // (a * b)
        if c == 0:
            break

        # print(a, b, c - b + 1)
        cnt += (c - b) + 1


print(cnt)
