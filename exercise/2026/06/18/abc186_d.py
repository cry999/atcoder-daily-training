N = int(input())
(*A,) = map(int, input().split())
A.sort()
print(sum(A[i] * (2 * i + 1 - N) for i in range(N)))
