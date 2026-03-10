N = int(input())
(*A,) = map(int, input().split())
(*W,) = map(int, input().split())

max_weight = {}
total_weight = sum(W)

for i in range(N):
    max_weight[A[i]] = max(max_weight.get(A[i], 0), W[i])

print(total_weight - sum(max_weight.values()))
