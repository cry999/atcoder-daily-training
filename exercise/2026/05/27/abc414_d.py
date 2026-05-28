N, M = map(int, input().split())
(*X,) = map(int, input().split())

X.sort()

D = [X[i + 1] - X[i] for i in range(N - 1)]
D.sort()
# print(D)
for _ in range(M - 1):
    if not D:
        break
    D.pop()

print(sum(D))
