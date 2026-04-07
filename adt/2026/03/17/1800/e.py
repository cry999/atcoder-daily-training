from sortedcontainers import SortedSet

N = int(input())
(*A,) = map(int, input().split())

B = SortedSet(iterable=A, key=lambda x: -x)

ans = [0] * N
for a in A:
    k = B.bisect_left(a)
    ans[k] += 1

for a in ans:
    print(a)
