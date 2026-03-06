S = input()
T = input()

i = 0
while i < len(S) and i < len(T) and S[i] == T[i]:
    i += 1

if i == len(S) == len(T):
    print(0)
else:
    print(i + 1)
