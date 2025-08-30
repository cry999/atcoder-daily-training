N, X = map(int, input().split())

p = [-1] * (X + 1)
p[0] = 0

for i in range(N):
    a, b = map(int, input().split())

    for x in range(X, -1, -1):
        if p[x] != i:
            continue
        if x + a <= X:
            p[x + a] = i + 1
        if x + b <= X:
            p[x + b] = i + 1

# print(p)
if p[X] == N:
    print('Yes')
else:
    print('No')
