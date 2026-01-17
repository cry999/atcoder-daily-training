from collections import deque


T = int(input())

for _ in range(T):
    N = int(input())
    S = input()

    visited = [False] * (1 << N)
    queue = deque()
    queue.append(0)

    while queue:
        s = queue.popleft()

        for i in range(N):
            if s & (1 << i):
                continue
            ns = s | (1 << i)
            if S[ns - 1] == "1":
                # danger
                continue
            if visited[ns]:
                # visited
                continue
            visited[ns] = True
            if ns + 1 == (1 << N):
                # goal
                break
            queue.append(ns)
        else:
            continue
        break
    if visited[-1]:
        print("Yes")
    else:
        print("No")
