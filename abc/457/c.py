N, K = map(int, input().split())
L = [0] * N
A = [[] for _ in range(N)]

for i in range(N):
    L[i], *(A[i]) = map(int, input().split())

(*C,) = map(int, input().split())

K -= 1
X = 0
i = 0
while X + C[i] * L[i] <= K:
    X += C[i] * L[i]
    i += 1
# print(K, X, i)
# K は A[i] のどこかにある
print(A[i][(K - X) % L[i]])
