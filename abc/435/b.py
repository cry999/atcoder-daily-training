from itertools import combinations

N = int(input())
*A, = map(int, input().split())

c = [0] * (N+1)

for j in range(N):
    c[j+1] = c[j] + A[j]

cnt = 0
# print(A)
for left, right in combinations(range(N), 2):
    s = c[right+1] - c[left]
    # print(f'{left=}, {right=}, {s=}')
    cnt += all(s % A[i] > 0 for i in range(left, right+1))
    # print(all(s % A[i] > 0 for i in range(left, right+1)))
print(cnt)
