N = int(input())
(*A,) = map(int, input().split())

dp_from_left = [0] * N
dp_from_right = [0] * N
dp_from_left[0] = 1
dp_from_right[-1] = 1

for i in range(1, N):
    if A[i] > dp_from_left[i - 1]:
        dp_from_left[i] = dp_from_left[i - 1] + 1
    else:
        dp_from_left[i] = A[i]
# print(*dp_from_left)

for i in range(1, N):
    if A[-i - 1] > dp_from_right[-i]:
        dp_from_right[-i - 1] = dp_from_right[-i] + 1
    else:
        dp_from_right[-i - 1] = A[-i - 1]
# print(*dp_from_right)

print(max(min(dp_from_left[i], dp_from_right[i]) for i in range(N)))
