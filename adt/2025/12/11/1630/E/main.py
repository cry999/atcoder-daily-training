from typing import Generator
import sys
import os


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


H1, W1 = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H1)]

H2, W2 = map(int, input().split())
B = [list(map(int, input().split())) for _ in range(H2)]

# 全探索 (bit 全探索) で行けそう


def sum1(bit: int) -> int:
    '''bit の 1 の個数を返す'''
    ans = 0
    while bit:
        ans += bit & 1
        bit >>= 1
    return ans


def bit_generate(bit: int) -> Generator[int, None, None]:
    i = 0
    while bit:
        if bit & 1:
            yield i
        bit >>= 1
        i += 1
    return


def check(h_bit: int, w_bit: int) -> bool:
    for i2, i1 in enumerate(bit_generate(h_bit)):
        for j2, j1 in enumerate(bit_generate(w_bit)):
            if A[i1][j1] != B[i2][j2]:
                return False
    return True


for h_bit in range(1 << H1):
    # debug(f'h_bit: {h_bit:0{H1}b}')
    if sum1(h_bit) != H2:
        # debug(f'  continue: {sum1(h_bit)}')
        continue
    for w_bit in range(1 << W1):
        # debug(f'  w_bit: {w_bit:0{W1}b}')
        if sum1(w_bit) != W2:
            # debug(f'    continue: {sum1(w_bit)}')
            continue
        # debug(f'CHECK: h_bit: {h_bit:0{H1}b}, w_bit: {w_bit:0{W1}b}')
        if check(h_bit, w_bit):
            print('Yes')
            break
    else:
        continue
    break
else:
    print('No')
