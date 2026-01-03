N = int(input())

bit_digits = []
for i in range(N.bit_length()):
    if N & (1 << i):
        bit_digits.append(i)

for bit in range(1 << N.bit_count()):
    ans = 0
    for i, d in enumerate(bit_digits):
        if bit & (1 << i):
            ans |= 1 << d
    print(ans)
