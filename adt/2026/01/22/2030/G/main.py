from collections import deque


Q = int(input())

queue = deque()
for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        x, c = args
        queue.append((x, c))
    else:  # if q == 2:
        c = args[0]

        s = 0
        while c:
            xx, cc = queue[0]
            if c >= cc:
                queue.popleft()
            else:  # c < cc
                queue[0] = (xx, cc - c)

            s += xx * min(c, cc)
            c -= min(c, cc)
        print(s)
