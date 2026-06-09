L, R = map(int, input().split())


def snake_number(upper: int) -> int:
    d = 1
    n = 1
    ans = 0
    nums = [1 for i in range(1, 10)]
    while d * 10 < upper:
        d *= 10
        n += 1
        ans += sum(nums)
        nums = [nums[i] * (i + 1) for i in range(9)]

    msd = upper // d
    ans += sum(nums[i] for i in range(msd - 1))

    upper %= d
    d //= 10
    n -= 1
    nums = [nums[i] // (i + 1) for i in range(9)]

    return ans


print(snake_number(12))
print(snake_number(R), snake_number(L - 1))
