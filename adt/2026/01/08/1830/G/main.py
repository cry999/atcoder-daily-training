N = int(input())
(*a,) = map(int, input().split())

stack = [(0, 0)]
num = 0
for a in a:
    top, cnt = stack.pop()
    if top == a:
        if cnt + 1 < a:
            stack.append((a, cnt + 1))
            num += 1
        else:
            # cnt + 1 == a
            # この場合は消える
            num -= cnt
    else:
        stack.append((top, cnt))
        stack.append((a, 1))
        num += 1

    print(num)
