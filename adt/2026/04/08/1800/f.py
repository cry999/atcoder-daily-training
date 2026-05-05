S = input()
T = input()

i, j = 0, 0
op = 0
while i < len(S) and j < len(T):
    if S[i] == T[j]:
        i += 1
        j += 1
    elif S[i] == "A":
        i += 1
        op += 1
    elif T[j] == "A":
        j += 1
        op += 1
    else:
        op = -1
        break

while op >= 0 and i < len(S):
    if S[i] == "A":
        i += 1
        op += 1
    else:
        op = -1

while op >= 0 and j < len(T):
    if T[j] == "A":
        j += 1
        op += 1
    else:
        op = -1

print(op)
