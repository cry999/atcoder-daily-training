S = input()
T = []

i = 0
while i < len(S):
    T.append(S[i])
    while len(T) >= 3 and T[-3] == "A" and T[-2] == "B" and T[-1] == "C":
        T.pop(), T.pop(), T.pop()
    i += 1

print("".join(T))
