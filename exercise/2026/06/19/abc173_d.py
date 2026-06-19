N = int(input())
(*A,) = map(int, input().split())
A.sort(reverse=True)
print(sum(A[(i + 1) // 2] for i in range(N - 1)))
