from collections import defaultdict

N = int(input())
(*A,) = map(int, input().split())

left = defaultdict(int)
right = defaultdict(int)
for a in A[1:]:
    right[a] += 1

s = sum(left[i] * right[i] for i in range(N + 1))
ans = 0
for j in range(1, N - 1):
    right[A[j]] -= 1
    s -= left[A[j]]

    left[A[j - 1]] += 1
    s += right[A[j - 1]]

    ans += s - left[A[j]] * right[A[j]]

print(ans)
