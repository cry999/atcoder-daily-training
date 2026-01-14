K = int(input())  # 1
S = input()
T = input()

if len(S) == len(T) + 1:
    i, j = 0, 0
    while i < len(S) and j < len(T):
        if S[i] == T[j]:
            j += 1
        i += 1

    if (i == len(S) or i == len(S) - 1) and j == len(T):
        print("Yes")
    else:
        print("No")
elif len(S) + 1 == len(T):
    i, j = 0, 0
    while i < len(S) and j < len(T):
        if S[i] == T[j]:
            i += 1
        j += 1
    if i == len(S) and (j == len(T) or j == len(T) - 1):
        print("Yes")
    else:
        print("No")
elif len(S) == len(T):
    change = 0
    for s, t in zip(S, T):
        change += s != t
    if change <= 1:
        print("Yes")
    else:
        print("No")
else:
    print("No")
