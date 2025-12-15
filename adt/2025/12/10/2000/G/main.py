import os
import sys
from typing import Generator


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


def debug_matrix(M: list[list[str]]):
    debug('== M ==')
    debug('\n'.join(''.join(r) for r in M))


POLYOMINOS = [
    [[c for c in input()] for _ in range(4)] for _ in range(3)
]

if sum(row.count('#') for P in POLYOMINOS for row in P) != 16:
    print('No')
    exit()


def rotate(P: list[str], n: int) -> list[str]:
    B = [row[:] for row in P]
    for _ in range(n):
        T = [row[:] for row in B]
        for i in range(4):
            for j in range(4):
                B[3-j][i] = T[i][j]
    return B


def parallel_move(P: list[str], di: int, dj: int) -> (list[str], bool):
    if di <= -4 or 4 <= di:
        return [], False
    if dj <= -4 or 4 <= dj:
        return [], False

    B = [row[:] for row in P]
    if di >= 0:
        for _ in range(di):
            if '#' in B[-1]:
                return [], False
            for i in range(3):
                for j in range(4):
                    B[3-i][j] = B[2-i][j]
            for j in range(4):
                B[0][j] = '.'
    else:
        for _ in range(-di):
            if '#' in B[0]:
                return [], False
            for i in range(3):
                for j in range(4):
                    B[i][j] = B[i+1][j]
            for j in range(4):
                B[-1][j] = '.'
    if dj >= 0:
        for _ in range(dj):
            if '#' in [B[i][-1] for i in range(4)]:
                return [], False
            for j in range(3):
                for i in range(4):
                    B[i][3-j] = B[i][2-j]
            for i in range(4):
                B[i][0] = '.'
    else:
        for _ in range(-dj):
            if '#' in [B[i][0] for i in range(4)]:
                return [], False
            for j in range(3):
                for i in range(4):
                    B[i][j] = B[i][j+1]
            for i in range(4):
                B[i][-1] = '.'
    return B, True


def merge(
    M1: list[list[str]],
    M2: list[list[str]],
    M3: list[list[str]],
) -> (list[list[str]], bool):
    B = [['.']*4 for _ in range(4)]
    for m in [M1, M2, M3]:
        for i in range(4):
            for j in range(4):
                if m[i][j] == '.':
                    continue
                if B[i][j] == m[i][j] == '#':
                    return [], False
                B[i][j] = m[i][j]
    return B, True


def transformed(P: list[list[str]]) -> Generator[list[list[str]], None, None]:
    for deg in range(4):
        A = rotate(P, deg)
        for di in range(-3, 4):
            for dj in range(-3, 4):
                M, ok = parallel_move(A, di, dj)
                if not ok:
                    continue
                debug(f'=== deg: {deg}, di: {di}, dj: {dj} ===')
                debug_matrix(M)
                yield M


for M1 in transformed(POLYOMINOS[0]):
    for M2 in transformed(POLYOMINOS[1]):
        for M3 in transformed(POLYOMINOS[2]):
            M, ok = merge(M1, M2, M3)
            if ok:
                debug('=== M1 ===')
                debug_matrix(M1)
                debug('=== M2 ===')
                debug_matrix(M2)
                debug('=== M3 ===')
                debug_matrix(M3)
                print('Yes')
                exit()
print('No')
