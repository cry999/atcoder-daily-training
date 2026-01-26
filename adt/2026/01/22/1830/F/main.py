N, Q = map(int, input().split())

min_ver = 1

pc = [int(i > 0) for i in range(N + 1)]

for _ in range(Q):
    x, y = map(int, input().split())
    if x < min_ver:
        print(0)
        continue

    c = 0
    for i in range(min_ver, x + 1):
        c += pc[i]
        pc[i] = 0

    pc[y] += c
    print(c)

    min_ver = min(x + 1, y)
