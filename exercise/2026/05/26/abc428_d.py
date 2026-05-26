from math import isqrt

T = int(input())

for _ in range(T):
    c, d = map(int, input().split())

    suffix_min = c + 1
    suffix_max = c + d

    # suffix が k 桁である時、base = 10^(k-1)
    base = 1
    ans = 0
    while base <= suffix_max:
        # k 桁の suffix の取りうる範囲
        left_suffix = max(suffix_min, base)
        right_suffix = min(suffix_max, base * 10 - 1)

        if left_suffix <= right_suffix:
            pow10 = base * 10
            left = c * pow10 + left_suffix
            right = c * pow10 + right_suffix

            ans += isqrt(right) - isqrt(left - 1)

        base *= 10

    print(ans)
