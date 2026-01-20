N, Q = map(int, input().split())
S = input()

left = [0] * (N + 1)
right = [0] * (N + 1)

for p in range(N-1):
    if S[p] == S[p + 1]:
        left[p + 1] += 1
        right[p + 2] += 1

for p in range(N):
    left[p + 1] += left[p]
    right[p + 1] += right[p]

for _ in range(Q):
    l, r = map(int, input().split())

    print(right[r] - left[l - 1])
