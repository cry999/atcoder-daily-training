N, K = map(int, input().split())
(*A,) = map(int, input().split())

DIGIT = K.bit_length()

x = [0] * (DIGIT)

mask = 1
for i in range(DIGIT):
    bit_cnt = 0
    for a in A:
        if a & mask:
            bit_cnt += 1

    if 2 * bit_cnt < N:
        x[i] = 1
    mask <<= 1

mask = 0
for i in range(DIGIT):
    mask <<= 1
    mask |= x[DIGIT - i - 1]

ans = sum(a ^ K for a in A)

for i in range(DIGIT):
    if K & (1 << i):
        x = 0
        # i ビットより上位は K と同じ
        for j in range(i + 1, DIGIT):
            if K & (1 << j):
                x |= 1 << j
        # i ビットは 0 にする
        # i ビットより下位は 1 にする
        for j in range(i):
            if mask & (1 << j):
                x |= 1 << j

        ans = max(ans, sum(a ^ x for a in A))

print(ans)
