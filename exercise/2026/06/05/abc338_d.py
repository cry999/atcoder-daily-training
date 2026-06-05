N, M = map(int, input().split())
(*X,) = map(int, input().split())

bridges = [0] * (N + 1)

for i in range(M - 1):
    x1, x2 = X[i], X[i + 1]
    x1, x2 = min(x1, x2), max(x1, x2)

    bridges[x1] += N - (x2 - x1)
    bridges[x2] -= N - (x2 - x1)

    bridges[x2] += x2 - x1
    bridges[0] += x2 - x1
    bridges[x1] -= x2 - x1

for i in range(N):
    bridges[i + 1] += bridges[i]

print(min(bridges[1:]))
# print(bridges[1:])
