N, X = map(int, input().split())
S = input()

stack = []
for s in S:
    if s == "U":
        if stack and stack[-1] != s:
            stack.pop()
        else:
            stack.append(s)
    else:
        stack.append(s)

cur = X
for s in stack:
    if s == "U":
        cur //= 2
    elif s == "L":
        cur *= 2
    else:
        cur = 2 * cur + 1
print(cur)
