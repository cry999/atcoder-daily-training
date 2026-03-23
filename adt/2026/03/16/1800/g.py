from sortedcontainers import SortedList

N, K = map(int, input().split())
(*P,) = map(int, input().split())

queue = SortedList(P[:K])

for i in range(N - K + 1):
    print(queue[i])
    if i + K < N:
        queue.add(P[i + K])
