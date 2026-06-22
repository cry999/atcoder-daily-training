from sortedcontainers import SortedList

N, M = map(int, input().split())
A = SortedList(map(int, input().split()))

for _ in range(M):
    a = A.pop()
    A.add(a // 2)

print(sum(A))
