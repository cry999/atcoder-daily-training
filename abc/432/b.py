X = sorted(input())
i = 0
while X[i] == '0':
    i += 1
X[i], X[0] = X[0], X[i]
print(''.join(X))
