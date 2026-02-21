from collections import deque

T = int(input())
q = deque()

for _ in range(T):
    N, D = map(int, input().split())
    (*A,) = map(int, input().split())
    (*B,) = map(int, input().split())

    for i in range(N):
        a, b = A[i], B[i]
        # morning
        q.append((a, i))

        # lunch
        while b:
            egg, d = q[0]
            if egg > b:
                q[0] = (egg - b, d)
                b = 0
            else:
                q.popleft()
                b = b - egg

        # evening
        while q:
            egg, d = q[0]
            if i - D < d:
                break
            q.popleft()  # dispose

    ans = 0
    while q:
        egg, _ = q.popleft()
        ans += egg
    print(ans)
