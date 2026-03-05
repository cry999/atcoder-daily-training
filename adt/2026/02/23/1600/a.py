N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

print(sum(A[b - 1] for b in B))
