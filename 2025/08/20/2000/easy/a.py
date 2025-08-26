S = input()

for i in range(len(S)):
    c = S[i]
    if c.isupper():
        print(i + 1)
