N, K = map(int, input().split())
A = list(map(int, input().split()))

lo, hi = max(A) // K, max(A)
border = 0
times = 60
while times:
    times -= 1

    mid = (lo+hi)/2
    k = sum(a // mid for a in A)
    if k >= K:
        lo = mid
        border = max(border, mid)
    else:
        hi = mid

# print(lo, hi)
# print(sum(a//border for a in A))
print(*[int(a/border) for a in A])


# # Priority Queue を使ってシミュレーション
# # Priority Queue を使った解法だと O(K logN) で K=10^9 のケースで間に合わない
#
# import heapq
#
# seats = [0]*N
# queue = []  # (-votes/(seats[i]+1), index)
#
# for i, a in enumerate(A):
#     heapq.heappush(queue, (-a, i))
#
# k = K
# while k:
#     k -= 1
#
#     _, idx = heapq.heappop(queue)
#     seats[idx] += 1
#     divs = seats[idx]
#     heapq.heappush(queue, (-A[idx]/(divs+1), idx))
#
# print(*seats)
