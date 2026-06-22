N = int(input())
(*A,) = map(int, input().split())

x = [0] * N
for i in range(N):
    if i % 2 == 0:
        x[0] += A[i]
    else:
        x[0] -= A[i]
x[0] //= 2

for i in range(1, N):
    x[i] = A[i - 1] - x[i - 1]

for i in range(N):
    x[i] *= 2

print(*x)
