S = input()
T = input()

i, j = 0, 0
while i < len(S) and j < len(T):
    s = S[i]
    cs = 1
    while i + 1 < len(S) and S[i + 1] == s:
        cs += 1
        i += 1

    t = T[j]
    ct = 1
    while j + 1 < len(T) and T[j + 1] == t:
        ct += 1
        j += 1

    if s != t:
        print("No")
        break

    if cs == 1 and ct != cs:
        print("No")
        break

    if cs > ct:
        print("No")
        break
    i += 1
    j += 1
else:
    if i == len(S) and j == len(T):
        print("Yes")
    else:
        print("No")
