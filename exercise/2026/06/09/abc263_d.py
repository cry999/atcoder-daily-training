N, L, R = map(int, input().split())
(*A,) = map(int, input().split())

left = [float("inf")] * (N + 1)
left[0] = 0

for i in range(N):
    left[i + 1] = min(left[i] + A[i], (i + 1) * L)

right = [float("inf")] * (N + 1)
right[N] = 0

for i in range(N - 1, -1, -1):
    right[i] = min(right[i + 1] + A[i], (N - i) * R)

print(min(l + r for l, r in zip(left, right)))
