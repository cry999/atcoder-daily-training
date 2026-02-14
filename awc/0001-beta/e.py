from sortedcontainers import SortedList

N, K = map(int, input().split())
(*H,) = map(int, input().split())

queue = SortedList(H[:K])
ans = queue[-1] - queue[0]

for i in range(N - K):
    queue.remove(H[i])
    queue.add(H[i + K])

    ans = max(ans, queue[-1] - queue[0])
print(ans)
