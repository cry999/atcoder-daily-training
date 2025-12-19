from collections import deque


UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3


def next_dir(dir: int, op: str) -> int:
    if op == 'A':
        return dir ^ 1
    if op == 'B':
        return dir ^ 3
    return dir ^ 2


def rev(dir: int) -> int:
    return dir ^ 1


def move(i: int, j: int, dir: int) -> tuple[int, int]:
    return i+(dir == DOWN or -(dir == UP)), j+(dir == RIGHT or -(dir == LEFT))


T = int(input())

for _ in range(T):
    H, W = map(int, input().split())
    S = [input() for _ in range(H)]

    queue = deque([(0, 0, 0, LEFT)])
    dp = [[[float('inf')]*4 for _ in range(W)] for _ in range(H)]
    dp[0][0][LEFT] = 0

    while queue:
        ops, i, j, dir = queue.popleft()
        for c in 'ABC':
            ndir = next_dir(dir, c)
            ni, nj = move(i, j, ndir)
            if not (0 <= ni < H and 0 <= nj < W):
                continue

            nops = dp[i][j][dir] + (S[i][j] != c)
            if nops < dp[ni][nj][rev(ndir)]:
                dp[ni][nj][rev(ndir)] = nops
                if S[i][j] == c:
                    queue.appendleft((nops, ni, nj, rev(ndir)))
                else:
                    queue.append((nops, ni, nj, rev(ndir)))

    ans = min(
        dp[-1][-1][LEFT]+(S[-1][-1] != 'A'),
        dp[-1][-1][UP]+(S[-1][-1] != 'B'),
    )
    print(ans)
