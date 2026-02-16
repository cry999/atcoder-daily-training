N, M, K = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

ans = []
for b in B:
    if A[b - 1] < K:
        ans.append(A[b - 1])

print(len(ans), sum(ans))
