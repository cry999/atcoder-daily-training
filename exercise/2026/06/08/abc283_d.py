S = input()
box = [False] * 26
stack = []

for s in S:
    if s == ")":
        while stack:
            c = stack.pop()
            if c == "(":
                break
            n = ord(c) - ord("a")
            box[n] = False
    else:
        stack.append(s)
        n = ord(s) - ord("a")
        if 0 <= n < 26:
            if box[n]:
                print("No")
                break
            box[n] = True
else:
    print("Yes")
