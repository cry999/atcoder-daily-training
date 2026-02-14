from sortedcontainers import SortedList

N, D = map(int, input().split())
(*A,) = map(int, input().split())

nums = SortedList()
l, r = 0, -1
ans = 0
while l < N and r < N:
    if r < l:
        nums.add(A[l])
        # print(f"  append: {A[l]}: {nums}")
        r = l

    while r + 1 < N:
        a = A[r + 1]
        i = nums.bisect_left(a)
        if i > 0 and a - nums[i - 1] < D:
            break
        if i < len(nums) and nums[i] - a < D:
            break
        nums.add(a)
        r += 1

    # print(l, r, nums)
    ans += max(0, r - l + 1)

    if nums:
        nums.remove(A[l])
        # print(f"  remove: {A[l]}: {nums}")

    l += 1

print(ans)
