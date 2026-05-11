S = input()
stack = []

open_bra = {")": "(", "]": "[", ">": "<"}

for s in S:
    if s in "([<":
        stack.append(s)
    elif s in ")]>" and stack and stack[-1] == open_bra[s]:
        stack.pop()
    else:
        print("No")
        break
else:
    if stack:
        print("No")
    else:
        print("Yes")
