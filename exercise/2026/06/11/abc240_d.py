N = int(input())
(*A,) = map(int, input().split())

stack = []
ball = 0

for a in A:
    ball += 1
    if stack and stack[-1][0] == a:
        stack[-1][1] += 1
        if stack[-1][1] == a:
            stack.pop()
            ball -= a
    else:
        stack.append([a, 1])
    print(ball)
