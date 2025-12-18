import heapq
import os
import sys


DEBUG = os.environ.get("DEBUG", "0") == "1"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]
B = [list(map(int, input().split())) for _ in range(H)]


def swap_row(A: list[list[int]], i: int, j: int) -> list[list[int]]:
    M = [row[:] for row in A]
    M[i], M[j] = M[j], M[i]
    return M


def transpose(A: list[list[int]]) -> list[list[int]]:
    H, W = len(A), len(A[0])
    M = [[0]*H for _ in range(W)]
    for i in range(H):
        for j in range(W):
            M[j][i] = A[i][j]
    return M


def swap_col(A: list[list[int]], i: int, j: int) -> list[list[int]]:
    return transpose(swap_row(transpose(A), i, j))


def equal(A: list[list[int]], B: list[list[int]]) -> bool:
    H, W = len(A), len(A[0])
    for i in range(H):
        for j in range(W):
            if A[i][j] != B[i][j]:
                return False
    return True


memo = {}


def memorable(A: list[list[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(row) for row in A)


queue = [(0, A, [])]
ans = []
while queue:
    def p(*args, **kwargs):
        debug(''*d, *args, **kwargs)

    d, M, ops = heapq.heappop(queue)
    if d > 22:
        continue

    ma = memorable(M)
    if ma in memo:
        continue
    memo[ma] = True

    if equal(M, B):
        ans = ops
        continue

    # swap rows
    for i in range(H-1):
        j = i+1
        # 元に戻す行為は無駄
        op = (0, i, j)
        if ops and op == ops[-1]:
            continue
        heapq.heappush(queue, (d+1, swap_row(M, i, j), ops+[op]))
    # swap cols
    for i in range(W-1):
        j = i+1
        op = (1, i, j)
        # 元に戻す行為は無駄
        if ops and op == ops[-1]:
            continue
        heapq.heappush(queue, (d+1, swap_col(M, i, j), ops+[op]))


mb = memorable(B)
print(len(ans) if mb in memo else -1)

if mb not in memo or not DEBUG:
    exit()


def debug_matrix(M: list[list[int]]):
    for row in M:
        debug(' '.join(map(str, row)))


debug('=== A:')
debug_matrix(A)

debug('=== B:')
debug_matrix(B)

debug('=== simulate:')
for op in ans:
    t, i, j = op
    if t == 0:
        A = swap_row(A, i, j)
        debug(f'  swap row {i} {j}')
    elif t == 1:
        A = swap_col(A, i, j)
        debug(f'  swap col {i} {j}')
    debug_matrix(A)

debug('=== B:')
debug_matrix(B)
