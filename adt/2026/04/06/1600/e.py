K = int(input())  # K == 1
S = input()
T = input()

i, j, op = 0, 0, 0
while i < len(S) and j < len(T):
    if S[i] == T[j]:
        i += 1
        j += 1
    elif op < K:
        if len(S) < len(T):
            # insert
            j += 1
        elif len(S) > len(T):
            # delete
            i += 1
        else:
            # replace
            i += 1
            j += 1
        op += 1
    else:
        break

if (len(S) - i) + (len(T) - j) + op <= K:
    print("Yes")
else:
    print("No")
