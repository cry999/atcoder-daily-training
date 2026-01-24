from sortedcontainers import SortedList


N, K = map(int, input().split())
(*a,) = map(int, input().split())
b = a[:]

a.sort()

for i in range(K):
    q = SortedList()
    j = i
    while j < N:
        q.add(b[j])
        j += K

    for j, v in enumerate(q):
        b[i + j * K] = v

# print(a, b)
for i in range(N):
    if a[i] != b[i]:
        print("No")
        break
else:
    print("Yes")
