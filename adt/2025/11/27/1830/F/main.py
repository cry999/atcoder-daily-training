N = int(input())

m = {}
n = N
# i: 短縮した数字のビットの位置
# j: N の立っているビットの位置
i, j = 0, 0
while n:
    if n & 1:
        m[j] = i
        i += 1
    j += 1
    n >>= 1

for b in range(1 << len(m)):
    a = 0
    for j, i in m.items():
        a |= ((b >> i) & 1) << j
    print(a)
