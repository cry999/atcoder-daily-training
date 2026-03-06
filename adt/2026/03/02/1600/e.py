N = int(input()) - 1

# 5 進数を 0,1,2,3,4 ではなく 0,2,4,6,8 で表す。

digits = []
while True:
    digits.append((N % 5) * 2)
    N //= 5
    if not N:
        break

print("".join(map(str, digits[::-1])))
