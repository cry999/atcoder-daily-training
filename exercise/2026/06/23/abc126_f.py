from collections import deque

M, K = map(int, input().split())


def solve():
    N = 1 << M
    if K >= N:
        return [-1]

    if M == 0:
        return [0, 0]

    if M == 1:
        return [0, 0, 1, 1] if K == 0 else [-1]

    ans = deque([K])
    for i in range(1, N):
        if i == K:
            continue
        ans.append(i)
        ans.appendleft(i)

    if K != 0:
        ans.append(0)
    ans.append(K)
    if K != 0:
        ans.append(0)

    return list(ans)


print(*solve())
