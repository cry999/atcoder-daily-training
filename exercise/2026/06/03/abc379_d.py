from collections import deque

Q = int(input())

offset = 0
planters = deque()
for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        planters.append(-offset)
    elif q == 2:
        T = args[0]
        offset += T
    else:  # q == 3
        H = args[0]
        ans = 0
        while planters and planters[0] + offset >= H:
            planters.popleft()
            ans += 1
        print(ans)
