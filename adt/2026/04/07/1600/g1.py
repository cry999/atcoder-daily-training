a, b, C = map(int, input().split())
X, Y = 0, 0

c1 = C.bit_count()
c0 = 60 - c1

if a + b < c1 or (a + b - c1) % 2:
    print(-1)
    exit()

# k: c1 を利用して X, Y のいずれかの 1 を立てた後に残った X, Y の 1 を立てるための 0 の個数
k = (a + b - c1) // 2
if not 0 <= k <= min(c0, a, b):
    print(-1)
    exit()

a, b = a - k, b - k
X, Y = 0, 0
for i in range(60):
    if C & (1 << i):
        if b:
            Y |= 1 << i
            b -= 1
        else:
            X |= 1 << i
            a -= 1
    elif k:
        X |= 1 << i
        Y |= 1 << i
        k -= 1
print(X, Y)
