a, b, C = map(int, input().split())

# c1: C を 2 進数に変換した時の 1 の個数
c1 = C.bit_count()
# c0: C を 2 進数 (60 桁) に変換した時の 0 の個数
c0 = 60 - c1

if a + b < c1 or (a + b - c1) % 2:
    # c0 の内 X, Y の両方のビットを立てるのに使う 0 の個数を k とすると
    # k = (a + b - c1) / 2 となる。この整数 k が存在しないなら失敗。
    print(-1)
    exit()

k = (a + b - c1) // 2
if not 0 <= k <= min(c0, a, b):
    print(-1)
    exit()

a, b = a - k, b - k
X, Y = 0, 0
for i in range(60):
    if C & (1 << i):
        # C[i] = 1 なら X, Y のどちらかのみに振り分ける
        if b:
            Y |= 1 << i
            b -= 1
        else:
            X |= 1 << i
            a -= 1
    elif k:
        # C[i] = 0 で k が残っているなら、X, Y 両方に 1 を振り分ける
        X |= 1 << i
        Y |= 1 << i
        k -= 1

print(X, Y)
