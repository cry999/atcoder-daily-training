Q = int(input())

stack = [0] * 100

for _ in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        x = args[0]
        stack.append(x)
    else:  # q == 2
        x = stack.pop()
        print(x)
