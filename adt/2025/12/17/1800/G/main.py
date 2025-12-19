N = int(input())
S = input()

open_stack = []
visible = [0] * (N+1)

for i, s in enumerate(S):
    if s == '(':
        open_stack.append(i)
    elif s == ')':
        if not open_stack:
            continue
        last_open = open_stack.pop()
        visible[last_open] -= 1
        visible[i+1] += 1

for i in range(N):
    visible[i+1] += visible[i]

print(''.join(S[i] for i in range(N) if visible[i] >= 0))
