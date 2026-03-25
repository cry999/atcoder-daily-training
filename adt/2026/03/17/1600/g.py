from collections import deque

A, N = map(int, input().split())

visited = set()
visited.add(N)

q = deque([(N, 0)])
while q:
    x, op = q.popleft()
    # print(x, op)
    if x == 1:
        print(op)
        break

    nx = x // A
    # print("  [div] ", nx)
    if x % A == 0 and nx not in visited:
        # print("  [div] added")
        visited.add(nx)
        q.append((nx, op + 1))

    nx = int(str(x)[1:] or "0") * 10 + int(str(x)[0])
    # print("  [rot] ", nx)
    if len(str(x)) == len(str(nx)) and nx % 10 != 0 and nx not in visited:
        # print("  [rot] added")
        visited.add(nx)
        q.append((nx, op + 1))
else:
    print(-1)
