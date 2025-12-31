S = list(input())
T = list(input())
X = []

while S != T:
    i = 0
    while i < len(S) and S[i] <= T[i]:
        i += 1
    if i == len(S):
        i -= 1
        while i >= 0 and S[i] >= T[i]:
            i -= 1

    S[i] = T[i]
    X.append(S[:])

print(len(X))
for x in X:
    print("".join(x))
