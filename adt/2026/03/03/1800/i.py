from collections import deque

H, W = map(int, input().split())
S = [list(map(lambda x: int(x) - 1, input().split())) for _ in range(H)]
G = [[i * W + j for j in range(W)] for i in range(H)]


def calc_state(S: list[list[int]]):
    res = 0
    for i in range(H):
        for j in range(W):
            res |= S[i][j] << (((i * W) + j) * 6)
    return res


def restore(state: int) -> list[list[int]]:
    res = [[0] * W for _ in range(H)]
    for i in range(H):
        for j in range(W):
            res[i][j] = state >> (((i * W) + j) * 6)
            res[i][j] %= 64
    return res


def operate(state: int, x: int, y: int):
    a = restore(state)
    b = restore(state)
    for i in range(H - 1):
        for j in range(W - 1):
            i1, j1 = i + x, j + y
            i2, j2 = H - i + x - 2, W - j + y - 2
            a[i1][j1] = b[i2][j2]
    return calc_state(a)


s = calc_state(S)
g = calc_state(G)

# T[i] := s からスタートして i 回操作することで到達できる状態
T = [set() for _ in range(11)]
T[0].add(s)

# U[i] := g からスタートして i 回操作することで到達できる状態
U = [set() for _ in range(11)]
U[0].add(g)


def search(start: int, state_set: list[set[int]]):
    visited = set()
    q = deque([(start, 0, 0)])
    while q:
        now, pre, op = q.popleft()

        for x in range(2):
            for y in range(2):
                next_state = operate(now, x, y)
                if pre == next_state:
                    continue
                if next_state in visited:
                    continue
                visited.add(next_state)
                state_set[op + 1].add(next_state)
                if op + 1 < 10:
                    q.append((next_state, now, op + 1))


search(s, T)
search(g, U)

ans = -1
for i in range(11):
    if T[i] & U[0]:
        ans = i
        break
else:
    for j in range(1, 11):
        if T[10] & U[j]:
            ans = 10 + j
            break

print(ans)
