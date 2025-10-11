S = input()

stack = []

for i, s in enumerate(S):
    if s == '(':
        stack.append(i+1)
    else:  # s == ')'
        j = stack.pop()
        print(j, i+1)
