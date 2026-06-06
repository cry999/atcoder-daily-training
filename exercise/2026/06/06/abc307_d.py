N = int(input())
S = input()

stack = []
open_num = 0

for s in S:
    if s == ")" and open_num:
        while stack:
            last = stack.pop()
            if last == "(":
                open_num -= 1
                break
    else:
        stack.append(s)
        open_num += s == "("

print("".join(stack))
