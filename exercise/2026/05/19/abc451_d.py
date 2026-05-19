# X[k] := k 桁の良い整数の集合
X = [set() for _ in range(10)]
# P[k] := k 桁の 2 冪の集合
P = [set() for _ in range(10)]

p = 1
k = 1
ten = 10
while p < 10**9:
    P[k].add(p)
    p *= 2
    if p >= ten:
        k += 1
        ten *= 10

X[0].add(0)

for k in range(1, 10):
    ten = 1
    for i in range(1, k + 1):
        ten *= 10
        X[k].update({x * ten + p for x in X[k - i] for p in P[i]})

A = []
for k in range(1, 10):
    A.extend(list(X[k]))
A.sort()

N = int(input())
print(A[N - 1])
