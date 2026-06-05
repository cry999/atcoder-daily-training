from sortedcontainers import SortedList

N = int(input())
(*H,) = map(int, input().split())

q = SortedList()

ans = [0] * N
for i in range(N - 1, -1, -1):
    ans[i] = len(q)

    while q and q[0] < H[i]:
        q.pop(0)

    q.add(H[i])

print(*ans)
