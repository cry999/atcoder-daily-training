a, b, C = map(int, input().split())
c = C.bit_count()

if a + b < c:
    print(-1)
    exit()

n = a + b - c
if n % 2 == 1:
    print(-1)
    exit()


m = n // 2  # C の 0 を両方に振り分ける回数
a1 = a - m  # C の 1 を a のみに振り分ける回数
b1 = b - m  # C の 1 を b のみに振り分ける回数
if a1 < 0 or b1 < 0:
    print(-1)
    exit()

X, Y = 0, 0

for i in range(61):
    if C & (1 << i):
        if a1:
            X |= 1 << i
            a1 -= 1
        elif b1:
            Y |= 1 << i
            b1 -= 1
    elif m:
        X |= 1 << i
        Y |= 1 << i
        m -= 1

if X >= 1 << 60 or Y >= 1 << 60:
    print(-1)
else:
    print(X, Y)
