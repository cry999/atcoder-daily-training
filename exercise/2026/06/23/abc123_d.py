import heapq

X, Y, Z, K = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())
(*C,) = map(int, input().split())

AB = [a + b for a in A for b in B]

AB.sort(reverse=True)
C.sort(reverse=True)

# (AB[i] + C[j], i, j)
used = set()
q = []
for i in range(Z):
    heapq.heappush(q, (-(AB[0] + C[i]), 0, i))
    used.add((0, i))


k = 0
while k < K:
    score, i, j = heapq.heappop(q)
    print(-score)
    k += 1
    if i + 1 < X * Y and (i + 1, j) not in used:
        heapq.heappush(q, (-(AB[i + 1] + C[j]), i + 1, j))
        used.add((i + 1, j))
    if j + 1 < Z and (i, j + 1) not in used:
        heapq.heappush(q, (-(AB[i] + C[j + 1]), i, j + 1))
        used.add((i, j + 1))
