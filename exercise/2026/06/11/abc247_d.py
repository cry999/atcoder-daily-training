from collections import deque

Q = int(input())
queue = deque()

for _ in range(Q):
    q, *args = map(int, input().split())

    # print(f"[DEBUG] before {queue=}")
    if q == 1:
        x, c = args
        queue.append((x, c))
    else:  # q == 2
        c = args[0]

        ans = 0
        while c > 0:
            x0, c0 = queue.popleft()
            ans += x0 * min(c, c0)
            if c >= c0:
                c -= c0
            else:
                queue.appendleft((x0, c0 - c))
                c = 0
        print(ans)
    # print(f"[DEBUG] after {queue=}")
