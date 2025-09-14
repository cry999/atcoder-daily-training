X, C = map(int, input().split())

# lo, hi = 0, X // 1000
# while lo <= hi:
#     m = (lo + hi) // 2
#     total = m*1000 + m * C
#     if total < X:
#         lo = m + 1
#     elif total > X:
#         hi = m - 1
#     else:
#         print(m)
#         exit()
#
# if lo*1000 + lo*C < X:
#     print(lo*1000)
# else:
#     print(hi*1000)

print((1000 * X) // (1000 + C) // 1000 * 1000)
