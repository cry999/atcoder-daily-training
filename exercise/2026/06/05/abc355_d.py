import sys

input = sys.stdin.readline

N = int(input())

L, R = [0] * N, [0] * N
for i in range(N):
    L[i], R[i] = map(int, input().split())

L.sort()
R.sort()

j = 0
ans = N * (N - 1) // 2
for i in range(N):
    while j < N and R[j] < L[i]:
        j += 1
    ans -= j

print(ans)


# from sortedcontainers import SortedList
#
# ranges = sorted(tuple(map(int, input().split())) for _ in range(N))
#
# old = SortedList()
#
# ans = 0
# for i, (l, r) in enumerate(ranges):
#     while old and old[0] < l:
#         old.pop(0)
#     ans += len(old)
#     old.add(r)
# print(ans)
