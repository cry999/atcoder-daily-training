S = input()
T = input()

i, j = 0, 0
op = 0
while i < len(S) and j < len(T):
    if S[i] == T[j]:
        i += 1
        j += 1
    elif S[i] == "A":
        op += 1
        i += 1
    elif T[j] == "A":
        op += 1
        j += 1
    else:
        op = -1
        break

while i < len(S) and op != -1:
    if S[i] == "A":
        op += 1
    else:
        op = -1
        break
    i += 1

while j < len(T) and op != -1:
    if T[j] == "A":
        op += 1
    else:
        op = -1
        break
    j += 1

print(op)
