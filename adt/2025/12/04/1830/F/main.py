import os


A = [list(map(int, input().split())) for _ in range(9)]

DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


VALID = list(range(1, 10))
for i in range(9):
    # 縦確認
    debug(f'checking {i}')
    debug(f'col {i}: {A[i]}')
    if list(sorted(A[i])) != VALID:
        debug(f'col {i} invalid: {A[i]}')
        print('No')
        break
    # 横確認
    debug(f'row {i}: {[A[j][i] for j in range(9)]}')
    if list(sorted(A[j][i] for j in range(9))) != VALID:
        debug(f'row {i} invalid: {[A[j][i] for j in range(9)]}')
        print('No')
        break
    oh = i//3
    ow = i % 3
    if list(sorted(A[j//3 + 3*oh][j % 3 + 3*ow] for j in range(9))) != VALID:
        debug(
            f'box {i} invalid: {[A[j//3 + 3*oh][j % 3 + 3*ow] for j in range(9)]}')
        print('No')
        break
else:
    print('Yes')
