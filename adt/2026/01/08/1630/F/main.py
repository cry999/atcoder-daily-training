N, R = map(int, input().split())
(*L,) = map(int, input().split())

left = 0
while left < R and L[left] == 1:
    left += 1

left_lock_cnt = 0
for i in range(left, R):
    left_lock_cnt += L[i]
left_door_cnt = R - left

right = N - 1
while R <= right and L[right] == 1:
    right -= 1

right_lock_cnt = 0
for i in range(R, right + 1):
    right_lock_cnt += L[i]
right_door_cnt = right - R + 1

# print(left, R, right)
# print(f"{left_lock_cnt=}, {left_door_cnt=}")
# print(f"{right_lock_cnt=}, {right_door_cnt=}")

ans = left_lock_cnt + left_door_cnt
ans += right_lock_cnt + right_door_cnt
print(ans)
