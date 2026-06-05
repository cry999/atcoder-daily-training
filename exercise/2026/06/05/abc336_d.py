N = int(input())
(*A,) = map(int, input().split())

left = [0] * N
left[0] = 1

for i in range(N - 1):
    left[i + 1] = min(A[i + 1], A[i] + 1, left[i] + 1)

# print(left)

right = [0] * N
right[-1] = 1
for i in range(N - 1, 0, -1):
    right[i - 1] = min(A[i - 1], A[i] + 1, right[i] + 1)

# print(right)

print(max(min(l, r) for l, r in zip(left, right)))
