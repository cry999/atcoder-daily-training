from collections import deque

S = deque(list(input()))
reverse = False

Q = int(input())
for _ in range(Q):
    q, *args = input().split()
    if q == "1":
        reverse = not reverse
    else:
        f, c = args
        if (f == "1" and not reverse) or (f == "2" and reverse):
            S.appendleft(c)
        else:
            S.append(c)

if reverse:
    print("".join(reversed(S)))
else:
    print("".join(S))
