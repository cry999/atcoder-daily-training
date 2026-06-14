T = int(input())

for _ in range(T):
    a, s = map(int, input().split())

    mask = 1
    carry = 0
    for i in range(60):
        s0 = s & mask
        a0 = a & mask
        c0 = carry
        if s0 and a0 and c0:
            # OK and carry
            carry = 1
        elif s0 and a0 and not c0:
            # NG
            break
        elif s0 and not a0 and c0:
            # OK and no carry
            carry = 0
        elif s0 and not a0 and not c0:
            # OK and no carry
            carry = 0
        elif not s0 and a0 and c0:
            # NG
            break
        elif not s0 and a0 and not c0:
            # OK and carry
            carry = 1
        elif not s0 and not a0 and c0:
            # OK and carry
            carry = 1
        else:  # all 0
            # OK and no carry
            carry = 0

        mask <<= 1
    else:
        print("Yes" if not carry else "No")
        continue

    print("No")
