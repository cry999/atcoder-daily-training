S = input()

stack = []
BRACKETS = {")": "(", "]": "[", ">": "<"}
for s in S:
    if s in BRACKETS and stack and stack[-1] == BRACKETS[s]:
        stack.pop()
    else:
        stack.append(s)

if stack:
    print("No")
else:
    print("Yes")
