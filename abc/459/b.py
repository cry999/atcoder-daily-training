N = int(input())
(*S,) = input().split()

C = []
for s in S:
    if s[0] in "abc":
        C.append(2)
    elif s[0] in "def":
        C.append(3)
    elif s[0] in "ghi":
        C.append(4)
    elif s[0] in "jkl":
        C.append(5)
    elif s[0] in "mno":
        C.append(6)
    elif s[0] in "pqrs":
        C.append(7)
    elif s[0] in "tuv":
        C.append(8)
    else:
        C.append(9)

print("".join(map(str, C)))
