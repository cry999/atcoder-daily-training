N = int(input())
*A, = map(int, input().split())
X = int(input())

sum_a = sum(A)

# まず、何個目(0-indexed)の A を利用しているのかを考える。
n = X // sum_a

X %= sum_a
lo, hi = 0, N
i = 0
while X >= 0:
    X -= A[i]
    i += 1

print(n*N + i)
