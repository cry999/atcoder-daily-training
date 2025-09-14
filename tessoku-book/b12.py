# # right を決めるための二分探索
#
# left, right = 1, 10**9
# while left <= right:
#     x = (left + right) // 2
#     if x**3 + x > 10**5:
#         right = x - 1
#     else:
#         left = x + 1
# print(left)  # 47

N = int(input())

left, right = 1, 47
while left + 0.00001 <= right:
    x = (left + right) / 2
    if x**3 + x > N:
        right = x
    else:
        left = x
print(left)

# print(left**3 + left)  # 確認用
# print(right**3 + right)  # 確認用
